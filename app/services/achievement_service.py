"""
AchievementService
==================
Dispatches rule checks from app/services/achievement_rules.py and manages
the unlock ledger. The dispatch loops here never change when a new
achievement is added — see achievement_rules.py for the Open/Closed core.

Idempotency: unlock() always pre-checks for an existing PlayerAchievement
row before inserting. None of the calling orchestration flows (game/
tournament/season finishing) are guaranteed to fire exactly once, so this
service must never assume single-fire hooks.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from app import db
from app.models import (
    Player, Game, Tournament, Season, TournamentParticipant,
    Achievement, PlayerAchievement, AchievementTrigger,
)
from app.services.achievement_rules import get_rules_for_trigger

logger = logging.getLogger(__name__)

MAX_PINNED = 3


@dataclass
class AchievementResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "AchievementResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "AchievementResult":
        return cls(ok=False, message=msg)


class AchievementService:

    # ── Core unlock ──────────────────────────────────────────────────────────

    @staticmethod
    def unlock(player_id: int, code: str, commit: bool = True) -> AchievementResult:
        achievement = db.session.query(Achievement).filter_by(code=code, is_active=True).first()
        if not achievement:
            return AchievementResult.fail(f"Достижение «{code}» не найдено или отключено.")

        existing = (
            db.session.query(PlayerAchievement)
            .filter_by(player_id=player_id, achievement_id=achievement.id)
            .first()
        )
        if existing:
            return AchievementResult.success("Уже получено.", data=existing)

        pa = PlayerAchievement(player_id=player_id, achievement_id=achievement.id)
        db.session.add(pa)
        if commit:
            db.session.commit()
        logger.info(f"Player #{player_id} unlocked achievement {code!r}")

        from app.services.bot_notify_service import BotNotifyService
        BotNotifyService.notify_player(
            player_id, "achievement-granted",
            {"achievement_name": achievement.name, "achievement_code": achievement.code},
        )

        return AchievementResult.success(f"Достижение «{achievement.name}» получено!", data=pa)

    # ── Dispatch hooks ───────────────────────────────────────────────────────

    @staticmethod
    def check_after_game(game: Game) -> List[AchievementResult]:
        rules = get_rules_for_trigger(AchievementTrigger.GAME)
        if not rules:
            return []
        context: dict = {"game": game}
        results = []
        for slot in game.slots:
            for rule in rules:
                try:
                    if rule.check(slot.player_id, context):
                        results.append(AchievementService.unlock(slot.player_id, rule.code, commit=False))
                except Exception:
                    logger.exception(f"Achievement rule {rule.code!r} failed for player #{slot.player_id}")
        db.session.commit()
        return results

    @staticmethod
    def check_after_tournament(tournament: Tournament) -> List[AchievementResult]:
        rules = get_rules_for_trigger(AchievementTrigger.TOURNAMENT)
        if not rules:
            return []
        from app.services.rating_service import RatingService
        context: dict = {
            "tournament": tournament,
            "ratings": RatingService.get_tournament_rating(tournament.id),
        }

        # Candidates = tournament participants ∪ fantasy drafters linked to a player
        # (a Fantasy drafter is explicitly NOT allowed to also be a participant,
        # so without the union, fantasy-only achievements would never fire).
        participant_ids = {
            p.player_id for p in
            db.session.query(TournamentParticipant).filter_by(tournament_id=tournament.id).all()
        }
        from app.models import FantasyDraft
        drafter_user_ids = [
            d.user_id for d in
            db.session.query(FantasyDraft).filter_by(tournament_id=tournament.id).all()
        ]
        drafter_player_ids = set()
        if drafter_user_ids:
            from app.models.user import User
            users = db.session.query(User).filter(User.id.in_(drafter_user_ids)).all()
            drafter_player_ids = {u.player_id for u in users if u.player_id}

        candidate_ids = participant_ids | drafter_player_ids
        results = []
        for player_id in candidate_ids:
            for rule in rules:
                try:
                    if rule.check(player_id, context):
                        results.append(AchievementService.unlock(player_id, rule.code, commit=False))
                except Exception:
                    logger.exception(f"Achievement rule {rule.code!r} failed for player #{player_id}")
        db.session.commit()
        return results

    @staticmethod
    def check_after_season(season: Season) -> List[AchievementResult]:
        rules = get_rules_for_trigger(AchievementTrigger.SEASON)
        if not rules:
            return []
        from app.services.season_rating_engine import SeasonRatingEngine
        context: dict = {
            "season": season,
            "ratings": SeasonRatingEngine.compute_season_ratings(season.id),
        }
        candidate_ids = {e.player_id for e in context["ratings"]}
        if season.winner_player_id:
            candidate_ids.add(season.winner_player_id)

        results = []
        for player_id in candidate_ids:
            for rule in rules:
                try:
                    if rule.check(player_id, context):
                        results.append(AchievementService.unlock(player_id, rule.code, commit=False))
                except Exception:
                    logger.exception(f"Achievement rule {rule.code!r} failed for player #{player_id}")
        db.session.commit()
        return results

    @staticmethod
    def check_after_purchase(player_id: int) -> List[AchievementResult]:
        rules = get_rules_for_trigger(AchievementTrigger.PURCHASE)
        if not rules:
            return []
        context: dict = {}
        results = []
        for rule in rules:
            try:
                if rule.check(player_id, context):
                    results.append(AchievementService.unlock(player_id, rule.code, commit=False))
            except Exception:
                logger.exception(f"Achievement rule {rule.code!r} failed for player #{player_id}")
        db.session.commit()
        return results

    # ── Queries ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_player_achievements(player_id: int) -> List[PlayerAchievement]:
        return (
            db.session.query(PlayerAchievement)
            .filter_by(player_id=player_id)
            .order_by(PlayerAchievement.unlocked_at.desc())
            .all()
        )

    @staticmethod
    def get_all_with_unlock_status(player_id: int) -> List[dict]:
        """2 queries total: all active achievements + this player's unlocks."""
        achievements = (
            db.session.query(Achievement)
            .filter_by(is_active=True)
            .order_by(Achievement.category, Achievement.rarity)
            .all()
        )
        unlocks = (
            db.session.query(PlayerAchievement)
            .filter_by(player_id=player_id)
            .all()
        )
        unlocked_map = {u.achievement_id: u for u in unlocks}

        out = []
        for a in achievements:
            unlock = unlocked_map.get(a.id)
            d = a.to_dict(unlocked=unlock is not None)
            d["unlocked_at"] = unlock.unlocked_at.isoformat() if unlock else None
            d["pinned"] = unlock.pinned if unlock else False
            out.append(d)
        return out

    # ── Pinning ──────────────────────────────────────────────────────────────

    @staticmethod
    def pin(player_id: int, achievement_id: int) -> AchievementResult:
        pa = (
            db.session.query(PlayerAchievement)
            .filter_by(player_id=player_id, achievement_id=achievement_id)
            .first()
        )
        if not pa:
            return AchievementResult.fail("Достижение ещё не получено.")
        if pa.pinned:
            return AchievementResult.success("Уже закреплено.", data=pa)

        pinned_count = (
            db.session.query(PlayerAchievement)
            .filter_by(player_id=player_id, pinned=True)
            .count()
        )
        if pinned_count >= MAX_PINNED:
            return AchievementResult.fail(f"Можно закрепить не более {MAX_PINNED} достижений.")

        used_orders = {
            p.pinned_order for p in
            db.session.query(PlayerAchievement).filter_by(player_id=player_id, pinned=True).all()
        }
        next_order = next(o for o in range(1, MAX_PINNED + 1) if o not in used_orders)

        pa.pinned = True
        pa.pinned_order = next_order
        db.session.commit()

        AchievementService.unlock(player_id, "pinned_first_achievement")

        return AchievementResult.success("Достижение закреплено.", data=pa)

    @staticmethod
    def unpin(player_id: int, achievement_id: int) -> AchievementResult:
        pa = (
            db.session.query(PlayerAchievement)
            .filter_by(player_id=player_id, achievement_id=achievement_id)
            .first()
        )
        if not pa:
            return AchievementResult.fail("Достижение не найдено.")
        pa.pinned = False
        pa.pinned_order = None
        db.session.commit()
        return AchievementResult.success("Открепление выполнено.", data=pa)

    # ── Admin manual grant (SPECIAL / MANUAL achievements) ───────────────────

    @staticmethod
    def admin_grant(player_id: int, code: str, reason: str) -> AchievementResult:
        if not reason or len(reason.strip()) < 3:
            return AchievementResult.fail("Укажите причину выдачи.")
        player = db.session.get(Player, player_id)
        if not player:
            return AchievementResult.fail("Игрок не найден.")
        result = AchievementService.unlock(player_id, code)
        if result.ok:
            logger.info(f"Admin granted achievement {code!r} to player #{player_id}: {reason}")
        return result
