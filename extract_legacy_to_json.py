"""
extract_legacy_to_json.py
==========================
Шаг 1 из 2 в переносе данных из старой версии приложения, когда старая БД и
новая система (например, PythonAnywhere) не имеют прямой сетевой видимости
друг друга (или вы просто не хотите держать Migration API включённым во
время всего чтения старой БД).

Этот скрипт НЕ шлёт ничего по сети — он только ЧИТАЕТ старую БД (через
SQLAlchemy reflection, как и migrate_from_legacy.py) и сохраняет данные в
статичные JSON-файлы локально. Дальше эти файлы нужно перенести (git,
загрузка файлов в PythonAnywhere, scp — как угодно) туда, где будет
запускаться import_legacy_json.py — второй скрипт, который уже отправляет
их в Migration API развёрнутого нового приложения.

────────────────────────────────────────────────────────────────────────
Как использовать
────────────────────────────────────────────────────────────────────────

1. Восстановить .sql-бэкап в любую реально доступную ВАМ ЛОКАЛЬНО MySQL
   (не обязательно ту же, что у новой системы):

       mysql -u root -p legacy_db < backup.sql

2. Задать переменную окружения и запустить:

       LEGACY_DATABASE_URL=mysql+pymysql://user:password@localhost/legacy_db
       python extract_legacy_to_json.py

   По умолчанию результат появится в папке ./legacy_export/:
   players.json, users.json, games.json, gg.json — каждый в формате
   {"items": [...]}, готовом для прямой отправки в Migration API.

3. Перенести папку legacy_export/ туда, где будете запускать
   import_legacy_json.py (см. докстринг того файла).

Предположения о старой схеме — те же, что и в migrate_from_legacy.py (см.
его докстринг): имена таблиц player/user/game/game_player/player_gg,
синтетический seat_number (в старой схеме реальной рассадки нет).

ВНИМАНИЕ: JSON-файлы содержат пароли пользователей в открытом виде (как
они хранились в старой БД) — храните и передавайте их так же осторожно,
как сам .sql-бэкап, и удалите после успешного импорта.
"""
from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import MetaData, create_engine, select

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("extract_legacy_to_json")

LEGACY_DATABASE_URL = os.environ.get(
    "LEGACY_DATABASE_URL", "mysql+pymysql://user:password@localhost/legacy_db"
)
OUTPUT_DIR = os.environ.get("LEGACY_EXPORT_DIR", "legacy_export")


def _iso(value: Any) -> Any:
    """
    Нормализует дату в ISO-строку вне зависимости от того, как её вернул
    конкретный DBAPI-драйвер (PyMySQL отдаёт datetime, некоторые
    окружения — уже готовую строку).
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _write(path: str, items: List[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False, indent=2, default=str)
    logger.info("Записано %d записей -> %s", len(items), path)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    engine = create_engine(LEGACY_DATABASE_URL)
    meta = MetaData()
    meta.reflect(bind=engine, only=["player", "user", "game", "game_player", "player_gg"])

    player_t = meta.tables["player"]
    user_t = meta.tables["user"]
    game_t = meta.tables["game"]
    game_player_t = meta.tables["game_player"]
    player_gg_t = meta.tables["player_gg"]

    with engine.connect() as conn:
        # ── Players ──────────────────────────────────────────────────────
        players = conn.execute(select(player_t).order_by(player_t.c.id)).mappings().all()
        logger.info("Старая БД: %d игроков", len(players))
        player_items = [{"legacy_id": row["id"], "name": row["name"]} for row in players]
        _write(os.path.join(OUTPUT_DIR, "players.json"), player_items)

        # ── Users (эффективный username = player.name, если привязан) ───
        users = conn.execute(
            select(user_t, player_t.c.name.label("_player_name"))
            .select_from(user_t.outerjoin(player_t, user_t.c.player_id == player_t.c.id))
            .order_by(user_t.c.id)
        ).mappings().all()
        logger.info("Старая БД: %d пользователей", len(users))
        user_items = []
        for row in users:
            effective_username = row["_player_name"] or row["_username"]
            user_items.append({
                "legacy_id": row["id"],
                "username": effective_username,
                "password": row["password"],
                "is_admin": bool(row["is_admin"]),
                "legacy_player_id": row["player_id"],
            })
        _write(os.path.join(OUTPUT_DIR, "users.json"), user_items)

        # ── Games + GamePlayer (группируем слоты по game_id) ─────────────
        games = conn.execute(select(game_t).order_by(game_t.c.id)).mappings().all()
        game_players = conn.execute(
            select(game_player_t).order_by(game_player_t.c.game_id, game_player_t.c.id)
        ).mappings().all()

        slots_by_game: Dict[int, list] = defaultdict(list)
        for gp in game_players:
            slots_by_game[gp["game_id"]].append(gp)

        logger.info("Старая БД: %d игр, %d слотов", len(games), len(game_players))
        game_items = []
        for g in games:
            raw_slots = slots_by_game.get(g["id"], [])
            if not raw_slots:
                logger.warning("Игра legacy_id=%s без слотов — пропускаю (не отправляю)", g["id"])
                continue
            # В старой БД изредка встречается один и тот же player_id дважды в
            # одной игре (похоже на баг редактирования в старом приложении —
            # правка роли/очков добавляла новую строку вместо обновления
            # старой). Строки этой игры уже отсортированы по возрастанию id
            # (см. ORDER BY выше), поэтому при дедупликации по player_id
            # оставляем последнюю встреченную — с наибольшим id, как более
            # позднюю/исправленную версию.
            deduped: Dict[int, Any] = {}
            for s in raw_slots:
                if s["player_id"] in deduped:
                    logger.warning(
                        "Игра legacy_id=%s: дубль player_id=%s в game_player "
                        "(id=%s заменяет id=%s) — оставляю более позднюю запись",
                        g["id"], s["player_id"], s["id"], deduped[s["player_id"]]["id"],
                    )
                deduped[s["player_id"]] = s
            slots = list(deduped.values())
            game_items.append({
                "legacy_id": g["id"],
                "played_at": _iso(g["date"]),
                "result": g["result"],
                "pu_guess": g["pu_guess"],
                "slots": [{
                    "legacy_player_id": s["player_id"],
                    "role": s["role"],
                    "seat_number": idx + 1,
                    "bonus_score": float(s["score"] or 0),
                    "is_pu": bool(s["pu_active"]),
                } for idx, s in enumerate(slots)],
            })
        _write(os.path.join(OUTPUT_DIR, "games.json"), game_items)

        # ── PlayerGG ──────────────────────────────────────────────────────
        gg_rows = conn.execute(select(player_gg_t).order_by(player_gg_t.c.id)).mappings().all()
        logger.info("Старая БД: %d GG-записей", len(gg_rows))
        gg_items = [{
            "legacy_id": row["id"],
            "legacy_player_id": row["player_id"],
            "amount": row["amount"],
            "date": _iso(row["date"]),
        } for row in gg_rows]
        _write(os.path.join(OUTPUT_DIR, "gg.json"), gg_items)

    logger.info("Готово. Перенесите папку %s/ туда, где будете запускать import_legacy_json.py", OUTPUT_DIR)


if __name__ == "__main__":
    main()
