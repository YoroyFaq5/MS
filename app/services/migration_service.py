"""
MigrationService
=================
Бизнес-логика одноразового Migration API (см. app/routes/migration.py) —
перенос данных из старой версии приложения. Переиспользует существующие
сервисы (AuthService, GGService, PostGameOrchestrator, SeasonService,
PlayerSearchService) — не создаёт объекты напрямую через SQL и не
дублирует их валидацию/бизнес-правила.

Идемпотентность: перед созданием каждой записи проверяется
LegacyImportMap (entity_type, legacy_id) — уже перенесённые записи
пропускаются («skipped»), без повторных побочных эффектов (важно для
Games — иначе повторный запуск снова прогнал бы PostGameOrchestrator и
задвоил ELO/монеты/достижения).

Устойчивость: каждая запись батча обрабатывается в своей try/except с
собственным commit/rollback — ошибка одной записи не прерывает импорт
остальных.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app import db
from app.models import Player, User, Game, GameSlot, Role, WinSide, LegacyImportMap
from app.services.auth_service import AuthService
from app.services.gg_service import GGService
from app.services.season_service import SeasonService
from app.services.orchestrator import PostGameOrchestrator
from app.services.player_search_service import PlayerSearchService

logger = logging.getLogger(__name__)

# Точные значения из старой БД (SELECT DISTINCT role/result) — подтверждены
# пользователем, не угадывались. Расширяется одной строкой при необходимости.
ROLE_MAP: Dict[str, Role] = {
    "мирный": Role.CIVILIAN,
    "мафия": Role.MAFIA,
    "дон": Role.DON,
    "шериф": Role.SHERIFF,
}
RESULT_MAP: Dict[str, WinSide] = {
    "black": WinSide.MAFIA,
    "red": WinSide.CITY,
}

# В старых PlayerGG нет поля "причина" — GGService.add_gg() требует ≥10
# символов, синтезируем фиксированную строку.
DEFAULT_GG_REASON = "Импортировано из старой системы"


def _parse_dt(value: Any) -> Optional[datetime]:
    """Принимает ISO-строку или datetime, всегда возвращает aware UTC."""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------

@dataclass
class ItemResult:
    legacy_id: Any
    status: str  # "imported" | "skipped" | "failed"
    new_id: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"legacy_id": self.legacy_id, "status": self.status}
        if self.new_id is not None:
            d["new_id"] = self.new_id
        if self.error:
            d["error"] = self.error
        return d


@dataclass
class BatchResult:
    imported: int = 0
    skipped: int = 0
    failed: int = 0
    results: List[ItemResult] = field(default_factory=list)

    def add(self, r: ItemResult) -> None:
        self.results.append(r)
        if r.status == "imported":
            self.imported += 1
        elif r.status == "skipped":
            self.skipped += 1
        else:
            self.failed += 1

    def to_dict(self) -> dict:
        return {
            "imported": self.imported,
            "skipped": self.skipped,
            "failed": self.failed,
            "results": [r.to_dict() for r in self.results],
        }


# ---------------------------------------------------------------------------
# MigrationService
# ---------------------------------------------------------------------------

class MigrationService:

    # ── Legacy map helpers ────────────────────────────────────────────────────

    @staticmethod
    def _find_new_id(entity_type: str, legacy_id: Any) -> Optional[int]:
        if legacy_id is None:
            return None
        row = (
            db.session.query(LegacyImportMap)
            .filter_by(entity_type=entity_type, legacy_id=legacy_id)
            .first()
        )
        return row.new_id if row else None

    @staticmethod
    def _record_map(entity_type: str, legacy_id: Any, new_id: int) -> None:
        db.session.add(LegacyImportMap(
            entity_type=entity_type, legacy_id=legacy_id, new_id=new_id,
        ))

    # ── Players ────────────────────────────────────────────────────────────────

    @staticmethod
    def import_players(items: List[dict]) -> BatchResult:
        batch = BatchResult()
        for item in items:
            legacy_id = item.get("legacy_id")
            try:
                if legacy_id is None:
                    raise ValueError("legacy_id обязателен")

                existing = MigrationService._find_new_id("player", legacy_id)
                if existing is not None:
                    batch.add(ItemResult(legacy_id, "skipped", new_id=existing))
                    continue

                name = (item.get("name") or "").strip()
                if not name:
                    raise ValueError("name обязателен")

                # Старая система хранила один-единственный идентификатор
                # (name). В новой схеме name обязателен и уникален, а
                # nickname — то, что реально отображается: переносим в оба.
                dupes = PlayerSearchService.find_exact_duplicates(name)
                if dupes:
                    logger.warning(
                        "[migration] player legacy_id=%s name=%r похож на "
                        "уже существующего игрока: %s",
                        legacy_id, name, [p.display_name for p in dupes],
                    )

                player = Player(
                    name=name,
                    nickname=name,
                    is_active=bool(item.get("is_active", True)),
                )
                created_at = _parse_dt(item.get("created_at"))
                if created_at:
                    player.created_at = created_at

                db.session.add(player)
                db.session.flush()  # получить player.id

                MigrationService._record_map("player", legacy_id, player.id)
                db.session.commit()
                batch.add(ItemResult(legacy_id, "imported", new_id=player.id))
            except Exception as e:
                db.session.rollback()
                logger.error("[migration] player legacy_id=%s failed: %s", legacy_id, e)
                batch.add(ItemResult(legacy_id, "failed", error=str(e)))

        logger.info(
            "[migration] players: imported=%d skipped=%d failed=%d",
            batch.imported, batch.skipped, batch.failed,
        )
        return batch

    # ── Users ──────────────────────────────────────────────────────────────────

    @staticmethod
    def import_users(items: List[dict]) -> BatchResult:
        batch = BatchResult()
        for item in items:
            legacy_id = item.get("legacy_id")
            try:
                if legacy_id is None:
                    raise ValueError("legacy_id обязателен")

                existing = MigrationService._find_new_id("user", legacy_id)
                if existing is not None:
                    batch.add(ItemResult(legacy_id, "skipped", new_id=existing))
                    continue

                username = (item.get("username") or "").strip()
                password = item.get("password") or ""
                if not username or not password:
                    raise ValueError("username и password обязательны")

                new_player_id = None
                legacy_player_id = item.get("legacy_player_id")
                if legacy_player_id is not None:
                    new_player_id = MigrationService._find_new_id("player", legacy_player_id)
                    if new_player_id is None:
                        raise ValueError(
                            f"игрок legacy_player_id={legacy_player_id} ещё не импортирован"
                        )

                # AuthService.register() хеширует пароль (User.set_password →
                # werkzeug) — старый plaintext-пароль продолжит работать.
                result = AuthService.register(
                    username=username,
                    password=password,
                    player_id=new_player_id,
                    migration_mode=True,
                )
                if not result.ok:
                    raise ValueError(result.message)

                user: User = result.data
                # register() всегда делает первого пользователя в системе
                # админом — перетираем реальным историческим значением,
                # каким бы оно ни было.
                user.is_admin = bool(item.get("is_admin", False))

                created_at = _parse_dt(item.get("created_at"))
                if created_at:
                    user.created_at = created_at
                last_login_at = _parse_dt(item.get("last_login_at"))
                if last_login_at:
                    user.last_login_at = last_login_at

                MigrationService._record_map("user", legacy_id, user.id)
                db.session.commit()
                batch.add(ItemResult(legacy_id, "imported", new_id=user.id))
            except Exception as e:
                db.session.rollback()
                logger.error("[migration] user legacy_id=%s failed: %s", legacy_id, e)
                batch.add(ItemResult(legacy_id, "failed", error=str(e)))

        logger.info(
            "[migration] users: imported=%d skipped=%d failed=%d",
            batch.imported, batch.skipped, batch.failed,
        )
        return batch

    # ── Games ──────────────────────────────────────────────────────────────────

    @staticmethod
    def import_games(items: List[dict]) -> BatchResult:
        batch = BatchResult()

        # Сезоны должны существовать до того, как PostGameOrchestrator
        # попытается привязать к ним игру — заранее гарантируем все года,
        # встречающиеся в батче (переиспользует SeasonService, не изобретает
        # новой логики создания сезонов).
        years = {
            _parse_dt(item.get("played_at")).year
            for item in items if item.get("played_at")
        }
        for year in years:
            SeasonService.ensure_year_exists(year)

        for item in items:
            legacy_id = item.get("legacy_id")
            try:
                if legacy_id is None:
                    raise ValueError("legacy_id обязателен")

                existing = MigrationService._find_new_id("game", legacy_id)
                if existing is not None:
                    batch.add(ItemResult(legacy_id, "skipped", new_id=existing))
                    continue

                played_at = _parse_dt(item.get("played_at"))
                if not played_at:
                    raise ValueError("played_at обязателен")

                result_raw = item.get("result")
                win_side = RESULT_MAP.get(result_raw)
                if win_side is None:
                    raise ValueError(f"Неизвестное значение result={result_raw!r}")

                slots_raw = item.get("slots") or []
                if not slots_raw:
                    raise ValueError("slots обязателен (минимум один игрок)")

                # Старый pu_guess — per-game (сколько мафий угадал ПУ-игрок),
                # в новой схеме это per-slot pu_mafia_count — ставим на слот
                # с is_pu=True.
                pu_guess = item.get("pu_guess")

                game = Game(
                    played_at=played_at,
                    win_side=win_side,
                    notes=item.get("notes"),
                    is_finished=True,
                    is_ranked=True,
                )
                db.session.add(game)
                db.session.flush()  # получить game.id для GameSlot.game_id

                for slot_raw in slots_raw:
                    legacy_player_id = slot_raw.get("legacy_player_id")
                    new_player_id = MigrationService._find_new_id("player", legacy_player_id)
                    if new_player_id is None:
                        raise ValueError(
                            f"игрок legacy_player_id={legacy_player_id} ещё не импортирован"
                        )

                    role_raw = slot_raw.get("role")
                    role = ROLE_MAP.get(role_raw)
                    if role is None:
                        raise ValueError(f"Неизвестное значение role={role_raw!r}")

                    is_pu = bool(slot_raw.get("is_pu", False))

                    db.session.add(GameSlot(
                        game_id=game.id,
                        player_id=new_player_id,
                        seat_number=slot_raw["seat_number"],
                        role=role,
                        base_score=0.0,  # пересчитает PostGameOrchestrator
                        bonus_score=float(slot_raw.get("bonus_score", 0.0)),
                        is_pu=is_pu,
                        pu_mafia_count=int(pu_guess) if (is_pu and pu_guess is not None) else 0,
                    ))

                db.session.flush()

                # Полный replay: новая формула очков/ELO, текущие правила
                # экономики, привязка к сезону, проверка достижений — тем
                # же путём, что и обычное завершение игры через UI.
                orch_result = PostGameOrchestrator.run(game)
                if orch_result.errors:
                    raise RuntimeError("; ".join(orch_result.errors))

                MigrationService._record_map("game", legacy_id, game.id)
                db.session.commit()
                batch.add(ItemResult(legacy_id, "imported", new_id=game.id))
            except Exception as e:
                db.session.rollback()
                logger.error("[migration] game legacy_id=%s failed: %s", legacy_id, e)
                batch.add(ItemResult(legacy_id, "failed", error=str(e)))

        logger.info(
            "[migration] games: imported=%d skipped=%d failed=%d",
            batch.imported, batch.skipped, batch.failed,
        )
        return batch

    # ── GG ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def import_gg(items: List[dict]) -> BatchResult:
        batch = BatchResult()

        years = {
            _parse_dt(item.get("date")).year
            for item in items if item.get("date")
        }
        for year in years:
            SeasonService.ensure_year_exists(year)

        for item in items:
            legacy_id = item.get("legacy_id")
            try:
                if legacy_id is None:
                    raise ValueError("legacy_id обязателен")

                existing = MigrationService._find_new_id("gg", legacy_id)
                if existing is not None:
                    batch.add(ItemResult(legacy_id, "skipped", new_id=existing))
                    continue

                legacy_player_id = item.get("legacy_player_id")
                new_player_id = MigrationService._find_new_id("player", legacy_player_id)
                if new_player_id is None:
                    raise ValueError(
                        f"игрок legacy_player_id={legacy_player_id} ещё не импортирован"
                    )
                player = db.session.get(Player, new_player_id)

                date = _parse_dt(item.get("date"))
                if not date:
                    raise ValueError("date обязателен")

                season = SeasonService.get_season_by_date(date)
                if not season:
                    raise ValueError(f"Не найден сезон для даты {date.isoformat()}")

                amount = item.get("amount")
                if amount is None:
                    raise ValueError("amount обязателен")

                gg_result = GGService.add_gg(
                    player=player,
                    season_id=season.id,
                    value=float(amount),
                    reason=item.get("reason") or DEFAULT_GG_REASON,
                    migration_mode=True,
                    commit=False,
                )
                if not gg_result.ok:
                    raise ValueError(gg_result.message)

                gg = gg_result.data
                gg.created_at = date  # сохраняем оригинальную дату начисления

                db.session.flush()
                MigrationService._record_map("gg", legacy_id, gg.id)
                db.session.commit()
                batch.add(ItemResult(legacy_id, "imported", new_id=gg.id))
            except Exception as e:
                db.session.rollback()
                logger.error("[migration] gg legacy_id=%s failed: %s", legacy_id, e)
                batch.add(ItemResult(legacy_id, "failed", error=str(e)))

        logger.info(
            "[migration] gg: imported=%d skipped=%d failed=%d",
            batch.imported, batch.skipped, batch.failed,
        )
        return batch
