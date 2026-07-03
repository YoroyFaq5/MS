"""
migrate_from_legacy.py
=======================
Скрипт-экстрактор для одноразового переноса данных из СТАРОЙ версии
приложения в новую, через уже существующий Migration API (/migration/*,
см. app/routes/migration.py + app/services/migration_service.py).

Этот скрипт НЕ парсит .sql-файл бэкапа напрямую (это ненадёжно — формат
mysqldump, экранирование, многострочные INSERT и т.п.) — вместо этого
подключается к УЖЕ ВОССТАНОВЛЕННОЙ из бэкапа живой MySQL-базе через
SQLAlchemy (reflection по именам таблиц/колонок) и читает данные обычными
SELECT'ами. Дальше просто переупаковывает строки в JSON и шлёт батчами в
уже готовый Migration API — вся бизнес-логика (проверки, ELO, экономика,
достижения) там же, здесь её нет и не должно быть.

────────────────────────────────────────────────────────────────────────
Как использовать
────────────────────────────────────────────────────────────────────────

1. Восстановить .sql-бэкап в ЛЮБУЮ реально доступную вам MySQL (не
   обязательно ту же, что у новой системы — можно локальную/временную):

       mysql -u root -p legacy_db < backup.sql

2. На новой системе временно включить Migration API (.env):

       MIGRATION_API_ENABLED=true
       MIGRATION_API_TOKEN=<длинный случайный секрет>

   и перезапустить новое приложение.

3. Задать переменные окружения для ЭТОГО скрипта (там, откуда он будет
   запускаться — там, где реально виден восстановленный legacy_db):

       LEGACY_DATABASE_URL=mysql+pymysql://user:password@host/legacy_db
       NEW_API_BASE_URL=http://127.0.0.1:5000       # адрес новой системы
       MIGRATION_API_TOKEN=<тот же секрет, что в п.2>

4. Запустить:

       python migrate_from_legacy.py

   Порядок отправки (players → users → games → gg) соблюдается сам —
   переставлять шаги местами не нужно и не следует (см. зависимости в
   MigrationService).

5. Проверить лог: сколько импортировано/пропущено/упало и почему
   (каждая проваленная запись — с legacy_id и причиной). Скрипт
   безопасно перезапускать — Migration API идемпотентен (уже
   импортированные записи будут пропущены, повторно не создадутся).

6. После успешного переноса — выключить MIGRATION_API_ENABLED в .env
   новой системы (или убрать переменную полностью).

────────────────────────────────────────────────────────────────────────
Предположения о старой схеме (может потребовать поправки под ваш реальный
дамп — см. SHOW TABLES / SHOW COLUMNS после восстановления бэкапа)
────────────────────────────────────────────────────────────────────────

Имена таблиц — дефолтные для Flask-SQLAlchemy (lowercase от имени
класса, без плюрализации): player, user, game, game_player, player_gg.

В старой схеме у GamePlayer нет номера места (seat_number) — в новой он
обязателен (1..10, уникален в пределах игры). Скрипт присваивает места
1..N в порядке выборки из БД (`ORDER BY id`) — это не реальная историческая
рассадка (её в старых данных просто нет), а технически необходимое
синтетическое значение для соответствия схеме новой системы.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List

from sqlalchemy import MetaData, create_engine, select

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("migrate_from_legacy")

LEGACY_DATABASE_URL = os.environ.get(
    "LEGACY_DATABASE_URL", "mysql+pymysql://user:password@localhost/legacy_db"
)
NEW_API_BASE_URL = os.environ.get("NEW_API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
MIGRATION_API_TOKEN = os.environ.get("MIGRATION_API_TOKEN")
BATCH_SIZE = 200


def _iso(value: Any) -> Any:
    """
    Нормализует дату в ISO-строку для JSON вне зависимости от того, как
    её вернул конкретный DBAPI-драйвер: PyMySQL обычно отдаёт настоящий
    datetime, но некоторые окружения/драйверы (в т.ч. использовались при
    тестировании этого скрипта на SQLite) отдают уже готовую строку —
    в этом случае просто передаём её как есть.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _chunks(seq: List[Any], size: int) -> Iterable[List[Any]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _post_batch(path: str, items: List[dict]) -> None:
    """POST одного батча в Migration API — тонкая обёртка, вся логика на стороне API."""
    if not items:
        return
    url = f"{NEW_API_BASE_URL}/migration/{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps({"items": items}, default=str).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MIGRATION_API_TOKEN}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw)
            message = body.get("message")
        except Exception:
            message = raw.decode("utf-8", "ignore")
        logger.error("HTTP %s при POST %s: %s", e.code, url, message)
        return
    except urllib.error.URLError as e:
        logger.error("Не удалось подключиться к %s: %s", url, e)
        return

    data = body.get("data", {}) or {}
    logger.info(
        "%s: imported=%s skipped=%s failed=%s",
        path, data.get("imported"), data.get("skipped"), data.get("failed"),
    )
    for r in data.get("results", []):
        if r.get("status") == "failed":
            logger.warning("  legacy_id=%s FAILED: %s", r.get("legacy_id"), r.get("error"))


def _run_batches(path: str, items: List[dict]) -> None:
    for batch in _chunks(items, BATCH_SIZE):
        _post_batch(path, batch)


def main() -> None:
    if not MIGRATION_API_TOKEN:
        sys.exit("MIGRATION_API_TOKEN не задан (см. докстринг файла).")

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
        _run_batches("players", player_items)

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
        _run_batches("users", user_items)

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
            slots = slots_by_game.get(g["id"], [])
            if not slots:
                logger.warning("Игра legacy_id=%s без слотов — пропускаю (не отправляю)", g["id"])
                continue
            game_items.append({
                "legacy_id": g["id"],
                "played_at": _iso(g["date"]),
                "result": g["result"],
                "pu_guess": g["pu_guess"],
                # Старая схема не хранит номер места — присваиваем по
                # порядку выборки (см. докстринг файла).
                "slots": [{
                    "legacy_player_id": s["player_id"],
                    "role": s["role"],
                    "seat_number": idx + 1,
                    "bonus_score": float(s["score"] or 0),
                    "is_pu": bool(s["pu_active"]),
                } for idx, s in enumerate(slots)],
            })
        _run_batches("games", game_items)

        # ── PlayerGG ──────────────────────────────────────────────────────
        gg_rows = conn.execute(select(player_gg_t).order_by(player_gg_t.c.id)).mappings().all()
        logger.info("Старая БД: %d GG-записей", len(gg_rows))
        gg_items = [{
            "legacy_id": row["id"],
            "legacy_player_id": row["player_id"],
            "amount": row["amount"],
            "date": _iso(row["date"]),
        } for row in gg_rows]
        _run_batches("gg", gg_items)

    logger.info("Готово.")


if __name__ == "__main__":
    main()
