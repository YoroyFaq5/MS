"""
FantasyService
==============
Fantasy draft system — entry-fee pool game (not FPL-style placement points).

Rules:
- User picks 3–5 players from a tournament they are NOT participating in.
  Pick count: ≤10 participants → 3, 11–16 → 4, 17+ → 5.
- Cannot pick yourself (if user.player_id is a tournament participant).
- Cannot change picks after tournament starts (LOCKED status).
- One draft per user per tournament.
- Anti-abuse: cannot create draft after tournament is finished.

Entry fee:
- Creating a draft costs EconomySettings.fantasy_entry_cost coins, charged
  immediately from the user's linked Player via EconomyService. Insufficient
  balance blocks draft creation. The amount actually charged is snapshotted
  on the draft (entry_cost_paid) so later admin price changes can't affect
  tournaments already in progress.

Scoring:
- A draft's total_points is the SUM of the real tournament rating points
  (RatingService.get_tournament_rating → PlayerRating.total_score) earned
  by its picked players — not a placement-based lookup table.

Prize pool:
- bank = sum of entry_cost_paid across all drafts of the tournament.
- Paid out once, when the tournament's drafts are scored: 1st place gets
  EconomySettings.fantasy_first_place_share of the bank, 2nd place gets
  fantasy_second_place_share. No coins are created beyond the bank.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from app import db
from app.models import (
    FantasyDraft, FantasyDraftPick, FantasyDraftStatus,
    Tournament, TournamentParticipant, Player,
    CoinSourceType,
)
from app.models.user import User

logger = logging.getLogger(__name__)


def _allowed_picks(participant_count: int) -> int:
    if participant_count <= 10:
        return 3
    if participant_count <= 16:
        return 4
    return 5


# ---------------------------------------------------------------------------
# Result DTO
# ---------------------------------------------------------------------------

@dataclass
class FantasyResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "FantasyResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "FantasyResult":
        return cls(ok=False, message=msg)


@dataclass
class FantasyLeaderboardEntry:
    rank: int
    user_id: int
    username: str
    display_name: str
    total_points: float
    pick_count: int
    draft_id: int

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "total_points": self.total_points,
            "pick_count": self.pick_count,
            "draft_id": self.draft_id,
        }


# ---------------------------------------------------------------------------
# FantasyService
# ---------------------------------------------------------------------------

class FantasyService:

    # ── Draft lifecycle ───────────────────────────────────────────────────────

    @staticmethod
    def create_draft(user: User, tournament_id: int) -> FantasyResult:
        """
        Create an OPEN draft for the user, charging the Fantasy entry fee.
        Validates: tournament active/pending, user not a participant, no
        existing draft, linked player with sufficient balance.
        """
        from app.services.economy_service import EconomyService

        t = db.session.get(Tournament, tournament_id)
        if not t:
            return FantasyResult.fail("Турнир не найден.")
        if t.status == "finished":
            return FantasyResult.fail("Нельзя создать драфт для завершённого турнира.")

        # Anti-abuse: one draft per tournament per user
        existing = db.session.query(FantasyDraft).filter_by(
            user_id=user.id, tournament_id=tournament_id
        ).first()
        if existing:
            return FantasyResult.fail("У вас уже есть драфт для этого турнира.")

        # Anti-abuse: user cannot draft their own tournament
        if user.player_id:
            is_participant = db.session.query(TournamentParticipant).filter_by(
                tournament_id=tournament_id, player_id=user.player_id
            ).first()
            if is_participant:
                return FantasyResult.fail(
                    "Вы не можете создать фэнтези-драфт для турнира, "
                    "в котором участвуете как игрок."
                )

        # Entry fee requires a linked player (coin balance lives on Player)
        if not user.is_player or not user.player:
            return FantasyResult.fail(
                "Для участия в Fantasy нужен привязанный профиль игрока."
            )

        entry_cost = EconomyService.get_settings().fantasy_entry_cost
        spend = EconomyService.spend_coins(
            user.player,
            entry_cost,
            f"Fantasy: вступительный взнос «{t.name}»",
            commit=False,
        )
        if not spend.ok:
            return FantasyResult.fail(spend.message)

        draft = FantasyDraft(
            user_id=user.id,
            tournament_id=tournament_id,
            status=FantasyDraftStatus.OPEN,
            entry_cost_paid=entry_cost,
        )
        db.session.add(draft)
        db.session.commit()
        return FantasyResult.success(
            f"Драфт для «{t.name}» создан, списано {entry_cost:.0f} монет. Выберите игроков.",
            data=draft,
        )

    @staticmethod
    def add_pick(user: User, draft_id: int, player_id: int) -> FantasyResult:
        """
        Add a player pick to an OPEN draft.
        Validates: pick limit, no duplicate, not self, not locked.
        """
        draft = db.session.get(FantasyDraft, draft_id)
        if not draft:
            return FantasyResult.fail("Драфт не найден.")
        if draft.user_id != user.id and not user.is_admin:
            return FantasyResult.fail("Доступ запрещён.")
        if draft.status != FantasyDraftStatus.OPEN:
            return FantasyResult.fail("Драфт зафиксирован — изменения невозможны.")

        # Pick limit
        participant_count = db.session.query(TournamentParticipant).filter_by(
            tournament_id=draft.tournament_id
        ).count()
        max_picks = _allowed_picks(participant_count)
        if len(draft.picks) >= max_picks:
            return FantasyResult.fail(
                f"Достигнут лимит выборов ({max_picks} для {participant_count} участников)."
            )

        player = db.session.get(Player, player_id)
        if not player or not player.is_active:
            return FantasyResult.fail("Игрок не найден.")

        # Cannot pick yourself
        if user.player_id == player_id:
            return FantasyResult.fail("Нельзя выбрать себя.")

        # Must be a tournament participant
        is_in_tourney = db.session.query(TournamentParticipant).filter_by(
            tournament_id=draft.tournament_id, player_id=player_id
        ).first()
        if not is_in_tourney:
            return FantasyResult.fail(
                f"«{player.display_name}» не участвует в этом турнире."
            )

        # No duplicate picks
        already = db.session.query(FantasyDraftPick).filter_by(
            draft_id=draft_id, player_id=player_id
        ).first()
        if already:
            return FantasyResult.fail(f"«{player.display_name}» уже в вашем драфте.")

        pick = FantasyDraftPick(draft_id=draft_id, player_id=player_id)
        db.session.add(pick)
        db.session.commit()
        return FantasyResult.success(
            f"«{player.display_name}» добавлен в драфт.", data=pick
        )

    @staticmethod
    def remove_pick(user: User, draft_id: int, player_id: int) -> FantasyResult:
        draft = db.session.get(FantasyDraft, draft_id)
        if not draft or (draft.user_id != user.id and not user.is_admin):
            return FantasyResult.fail("Доступ запрещён.")
        if draft.status != FantasyDraftStatus.OPEN:
            return FantasyResult.fail("Драфт зафиксирован.")

        pick = db.session.query(FantasyDraftPick).filter_by(
            draft_id=draft_id, player_id=player_id
        ).first()
        if not pick:
            return FantasyResult.fail("Выбор не найден.")

        db.session.delete(pick)
        db.session.commit()
        return FantasyResult.success("Игрок убран из драфта.")

    @staticmethod
    def lock_drafts_for_tournament(tournament_id: int, commit: bool = True) -> int:
        """
        Lock all OPEN drafts when a tournament starts.
        Call when tournament status transitions to 'active'.
        Returns count of locked drafts.
        """
        drafts = db.session.query(FantasyDraft).filter_by(
            tournament_id=tournament_id,
            status=FantasyDraftStatus.OPEN,
        ).all()
        for d in drafts:
            d.status = FantasyDraftStatus.LOCKED
        if commit:
            db.session.commit()
        logger.info(f"Locked {len(drafts)} fantasy drafts for tournament #{tournament_id}")
        return len(drafts)

    # ── Scoring ───────────────────────────────────────────────────────────────

    @staticmethod
    def score_tournament(tournament_id: int, commit: bool = True) -> List[FantasyResult]:
        """
        Score all unscored drafts of a finished tournament: each draft's
        total_points becomes the sum of its picks' real tournament rating
        points (RatingService.get_tournament_rating → total_score).

        Once every draft is SCORED, pays out the prize pool (sum of all
        entry_cost_paid) to 1st/2nd place per EconomySettings shares. This
        only fires the one time the tournament transitions from "has
        unscored drafts" to "fully scored" — calling this again afterwards
        is a no-op, so the payout can't be accidentally doubled.
        """
        from app.services.rating_service import RatingService
        from app.services.economy_service import EconomyService

        t = db.session.get(Tournament, tournament_id)
        if not t or t.status != "finished":
            return [FantasyResult.fail("Турнир не завершён.")]

        all_drafts = db.session.query(FantasyDraft).filter_by(
            tournament_id=tournament_id
        ).all()
        if not all_drafts:
            return [FantasyResult.fail("Нет Fantasy-драфтов для этого турнира.")]

        unscored = [d for d in all_drafts if d.status != FantasyDraftStatus.SCORED]
        if not unscored:
            return [FantasyResult.fail("Все драфты этого турнира уже подсчитаны.")]

        ratings = RatingService.get_tournament_rating(tournament_id)
        points_map = {r.player_id: r.total_score for r in ratings}

        results = []
        for draft in unscored:
            total = 0.0
            for pick in draft.picks:
                pts = points_map.get(pick.player_id, 0.0)
                pick.points_earned = round(pts, 2)
                total += pts

            draft.total_points = round(total, 2)
            draft.status = FantasyDraftStatus.SCORED
            draft.scored_at = datetime.now(timezone.utc)

            results.append(FantasyResult.success(
                f"Драфт #{draft.id} ({draft.user.username}): {draft.total_points} очков",
                data=draft,
            ))

        if commit:
            db.session.commit()

        from app.services.bot_notify_service import BotNotifyService
        for draft in unscored:
            if draft.user and draft.user.player_id:
                BotNotifyService.notify_player(
                    draft.user.player_id, "fantasy-result",
                    {"tournament_name": t.name, "points": draft.total_points},
                )

        # ── Prize pool payout ────────────────────────────────────────────
        bank = round(sum(d.entry_cost_paid for d in all_drafts), 2)
        if bank > 0:
            settings = EconomyService.get_settings()
            leaderboard = FantasyService.get_leaderboard(tournament_id)
            for place, share in (
                (1, settings.fantasy_first_place_share),
                (2, settings.fantasy_second_place_share),
            ):
                if share <= 0 or len(leaderboard) < place:
                    continue
                entry = leaderboard[place - 1]
                user = db.session.get(User, entry.user_id)
                if not (user and user.player):
                    continue
                amount = round(bank * share, 2)
                if amount <= 0:
                    continue
                EconomyService.add_coins(
                    user.player,
                    amount,
                    f"Fantasy место #{place} в «{t.name}» (банк {bank:.0f})",
                    CoinSourceType.FANTASY_REWARD,
                    ref_tournament_id=tournament_id,
                    commit=False,
                )
                BotNotifyService.notify_player(
                    user.player.id, "fantasy-prize",
                    {"tournament_name": t.name, "place": place, "amount": amount},
                )
            if commit:
                db.session.commit()

        return results

    @staticmethod
    def get_pool_info(tournament_id: int) -> dict:
        """
        Entry cost, participant count, current bank and projected payouts
        for the tournament's Fantasy page. Bank is the sum of what was
        actually charged to each draft (entry_cost_paid), so it stays
        correct even if the admin changes the entry cost mid-tournament.
        """
        from app.services.economy_service import EconomyService

        settings = EconomyService.get_settings()
        drafts = db.session.query(FantasyDraft).filter_by(
            tournament_id=tournament_id
        ).all()

        bank = round(sum(d.entry_cost_paid for d in drafts), 2)
        return {
            "entry_cost": settings.fantasy_entry_cost,
            "participant_count": len(drafts),
            "bank": bank,
            "payout_1st": round(bank * settings.fantasy_first_place_share, 2),
            "payout_2nd": round(bank * settings.fantasy_second_place_share, 2),
        }

    # ── Leaderboard ───────────────────────────────────────────────────────────

    @staticmethod
    def get_leaderboard(tournament_id: int) -> List[FantasyLeaderboardEntry]:
        drafts = (
            db.session.query(FantasyDraft)
            .filter_by(tournament_id=tournament_id)
            .order_by(FantasyDraft.total_points.desc())
            .all()
        )
        entries = []
        for rank, d in enumerate(drafts, start=1):
            user = d.user
            if not user:
                continue
            entries.append(FantasyLeaderboardEntry(
                rank=rank,
                user_id=user.id,
                username=user.username,
                display_name=user.display_name,
                total_points=d.total_points,
                pick_count=d.pick_count,
                draft_id=d.id,
            ))
        return entries

    @staticmethod
    def get_user_draft(user_id: int, tournament_id: int) -> Optional[FantasyDraft]:
        return db.session.query(FantasyDraft).filter_by(
            user_id=user_id, tournament_id=tournament_id
        ).first()

    @staticmethod
    def get_available_picks(user: User, tournament_id: int) -> List[Player]:
        """Players available for the user to pick (in tournament, not self, not already picked)."""
        draft = FantasyService.get_user_draft(user.id, tournament_id)
        already_picked = {p.player_id for p in draft.picks} if draft else set()

        participants = (
            db.session.query(TournamentParticipant)
            .filter_by(tournament_id=tournament_id)
            .all()
        )
        result = []
        for p in participants:
            if p.player_id == user.player_id:
                continue                    # cannot pick self
            if p.player_id in already_picked:
                continue
            if p.player and p.player.is_active:
                result.append(p.player)
        return sorted(result, key=lambda pl: pl.display_name)
