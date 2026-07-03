"""
GGService
=========
Manages admin-assigned "GG" bonuses — manual season-scoped point
adjustments. GG NEVER touches ELO or global rating. It only ever
feeds into SeasonRatingEngine.

Anti-abuse:
    - Every GG entry requires a non-trivial reason (>= 10 chars).
    - Every entry is attributed to an admin_id — full audit trail.
    - Entries are never deleted, only soft-revoked (revoked=True),
      preserving history for accountability.
    - A per-admin per-day cap limits total GG value granted, to
      prevent a single compromised/malicious admin account from
      mass-inflating one player's season score.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from app import db
from app.models import GG, Player, Season

logger = logging.getLogger(__name__)

MIN_REASON_LENGTH = 10
MAX_SINGLE_GG_VALUE = 50.0          # one entry cannot exceed this magnitude
DAILY_ADMIN_GG_CAP = 200.0          # total |value| an admin can grant per day


@dataclass
class GGResult:
    ok: bool
    message: str
    data: object = None

    @classmethod
    def success(cls, msg="OK", data=None) -> "GGResult":
        return cls(True, msg, data)

    @classmethod
    def fail(cls, msg: str) -> "GGResult":
        return cls(False, msg)


class GGService:

    # ── Add a GG bonus ────────────────────────────────────────────────────────

    @staticmethod
    def add_gg(
        player: Player,
        season_id: int,
        value: float,
        reason: str,
        admin_id: Optional[int] = None,
        commit: bool = True,
        migration_mode: bool = False,
    ) -> GGResult:
        """
        migration_mode: пропускает анти-абьюз лимиты (MAX_SINGLE_GG_VALUE,
        DAILY_ADMIN_GG_CAP) — они рассчитаны на защиту от живого
        злоупотребления администратором здесь-и-сейчас и бессмысленны при
        одноразовом переносе исторических данных пачкой. Проверка причины
        и существования сезона остаётся всегда. Используется только
        Migration API (см. migration_service.py).
        """
        if len(reason.strip()) < MIN_REASON_LENGTH:
            return GGResult.fail(
                f"Причина должна быть не короче {MIN_REASON_LENGTH} символов."
            )

        season = db.session.get(Season, season_id)
        if not season:
            return GGResult.fail("Сезон не найден.")

        if not migration_mode and abs(value) > MAX_SINGLE_GG_VALUE:
            return GGResult.fail(
                f"Одно начисление не может превышать ±{MAX_SINGLE_GG_VALUE}."
            )

        # Anti-abuse: daily cap per admin
        if not migration_mode and admin_id is not None:
            today_total = GGService._admin_daily_total(admin_id)
            if today_total + abs(value) > DAILY_ADMIN_GG_CAP:
                return GGResult.fail(
                    f"Превышен дневной лимит GG для администратора "
                    f"({today_total:.0f}/{DAILY_ADMIN_GG_CAP:.0f} уже использовано)."
                )

        gg = GG(
            player_id=player.id,
            season_id=season_id,
            value=round(value, 2),
            reason=reason.strip(),
            admin_id=admin_id,
        )
        db.session.add(gg)
        if commit:
            db.session.commit()

        logger.info(
            f"GG added: player#{player.id} season#{season_id} "
            f"value={value:+.2f} reason={reason!r} admin={admin_id}"
        )
        return GGResult.success(
            f"GG {'+' if value >= 0 else ''}{value} для «{player.display_name}» "
            f"в сезоне «{season.name}».",
            data=gg,
        )

    # ── Revoke (soft delete) ─────────────────────────────────────────────────

    @staticmethod
    def revoke_gg(gg_id: int) -> GGResult:
        gg = db.session.get(GG, gg_id)
        if not gg:
            return GGResult.fail("Запись GG не найдена.")
        if gg.revoked:
            return GGResult.fail("Запись уже отозвана.")
        gg.revoked = True
        db.session.commit()
        return GGResult.success("GG-бонус отозван.", data=gg)

    # ── Queries — strictly season-scoped, never cross-season ────────────────

    @staticmethod
    def get_season_gg(season_id: int) -> List[GG]:
        """All non-revoked GG entries for a single season. Never leaks across seasons."""
        return (
            db.session.query(GG)
            .filter(GG.season_id == season_id, GG.revoked == False)
            .order_by(GG.created_at.desc())
            .all()
        )

    @staticmethod
    def get_player_season_gg_total(player_id: int, season_id: int) -> float:
        """
        Sum of all active GG values for one player in one season.
        This is the ONLY function SeasonRatingEngine should call —
        guarantees GG from other seasons can never leak in.
        """
        entries = (
            db.session.query(GG)
            .filter(
                GG.player_id == player_id,
                GG.season_id == season_id,
                GG.revoked == False,
            )
            .all()
        )
        return round(sum(e.value for e in entries), 2)

    @staticmethod
    def get_player_gg_history(player_id: int) -> List[GG]:
        """Full GG history across all seasons — for profile/audit views only."""
        return (
            db.session.query(GG)
            .filter(GG.player_id == player_id)
            .order_by(GG.created_at.desc())
            .all()
        )

    # ── Anti-abuse helper ─────────────────────────────────────────────────────

    @staticmethod
    def _admin_daily_total(admin_id: int) -> float:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        entries = (
            db.session.query(GG)
            .filter(
                GG.admin_id == admin_id,
                GG.created_at >= today_start,
                GG.revoked == False,
            )
            .all()
        )
        return sum(abs(e.value) for e in entries)
