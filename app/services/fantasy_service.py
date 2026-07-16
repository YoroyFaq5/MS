"""
FantasyService
==============
Fantasy draft system — entry-fee pool game (not FPL-style placement points).

Rules:
- User picks players from a tournament they are NOT participating in.
  Pick count: ≤40 participants → 2, >40 → 5. Series-scoped drafts (one
  evening) instead use a fixed SERIES_PICKS_PER_DRAFTER (3), independent
  of tournament size — see the exclusivity-group rules below.
- Cannot pick yourself (if user.player_id is a tournament participant).
- Cannot change picks after tournament starts (LOCKED status).
- One draft per user per tournament.
- Anti-abuse: cannot create draft after tournament is finished.

Series exclusivity groups (see FantasyService._assign_group):
- Series drafts are split into groups of SERIES_GROUP_SIZE (3) drafters,
  filled in join order; a new group opens once the current one is full.
- Within a group, a player can only be picked by ONE drafter — enforced
  in add_pick and reflected in get_available_picks. The same player is
  freely pickable by a drafter in a different group.
- Each group has its own leaderboard and prize bank (drawn only from its
  own drafters' entry fees) — see score_series.

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

Practice mode (is_practice=True):
- Free — no entry fee charged, entry_cost_paid stays 0. Lets someone use
  the drafting tool (pick players, watch live points) without staking
  coins or competing for a payout.
- Fully separate universe from paid drafts: own leaderboard, own
  exclusivity groups (see _assign_group) — a practice group's picks never
  collide with a paid group's, and a practice draft can NEVER appear in
  the paid leaderboard used for prize payout (score_tournament/score_series
  filter is_practice=False explicitly, not just "bank > 0", since a
  practice draft mixed into a paid group's leaderboard could otherwise
  rank into a payout slot for free).
- A user may hold one paid AND one practice draft for the same
  tournament/series at once (the "one draft per user" uniqueness is keyed
  on (user, tournament, series, is_practice) — see the model).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func

from app import db
from app.models import (
    FantasyDraft, FantasyDraftPick, FantasyDraftStatus,
    Tournament, TournamentParticipant, Player,
    TournamentSeries, SeriesStatus,
    CoinSourceType,
)
from app.models.user import User

logger = logging.getLogger(__name__)

# Серийные (по вечеру) драфты используют фиксированный формат вместо
# масштабирования по числу участников турнира — группа эксклюзивности
# всегда SERIES_GROUP_SIZE драфтеров, каждый берёт SERIES_PICKS_PER_DRAFTER
# игроков (см. FantasyService._assign_group).
SERIES_GROUP_SIZE = 3
SERIES_PICKS_PER_DRAFTER = 3


def _allowed_picks(participant_count: int, is_series: bool = False) -> int:
    if is_series:
        return SERIES_PICKS_PER_DRAFTER
    if participant_count <= 40:
        return 2
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
    status: str = "open"
    group_number: Optional[int] = None
    picks: list = field(default_factory=list)  # [{"player_id", "display_name", "points_earned"}]

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "total_points": self.total_points,
            "pick_count": self.pick_count,
            "draft_id": self.draft_id,
            "status": self.status,
            "group_number": self.group_number,
            "picks": self.picks,
        }


# ---------------------------------------------------------------------------
# FantasyService
# ---------------------------------------------------------------------------

class FantasyService:

    # ── Draft lifecycle ───────────────────────────────────────────────────────

    @staticmethod
    def create_draft(
        user: User, tournament_id: int, tournament_series_id: Optional[int] = None,
        is_practice: bool = False,
    ) -> FantasyResult:
        """
        Create an OPEN draft for the user, charging the Fantasy entry fee
        (skipped entirely when is_practice=True — see module docstring).
        Validates: tournament active/pending, user not a participant, no
        existing draft, linked player (balance check skipped for practice).

        tournament_series_id (optional) scopes the draft to one series
        (game evening) inside a series-tournament instead of the whole
        tournament — picks are then scored off that series' stage rating
        (RatingService.get_stage_rating) rather than the tournament-wide
        one, with its own separate leaderboard/prize pool.
        """
        from app.services.economy_service import EconomyService

        t = db.session.get(Tournament, tournament_id)
        if not t:
            return FantasyResult.fail("Турнир не найден.")
        if t.status == "finished":
            return FantasyResult.fail("Нельзя создать драфт для завершённого турнира.")

        series: Optional[TournamentSeries] = None
        if tournament_series_id is not None:
            series = db.session.get(TournamentSeries, tournament_series_id)
            if not series or series.series_tournament.tournament_id != tournament_id:
                return FantasyResult.fail("Серия не найдена.")
            if series.status != SeriesStatus.ACTIVE:
                return FantasyResult.fail(
                    f"Драфт можно создать только для активной серии (сейчас: «{series.status.value}»)."
                )
            # Раз для серий нет отдельного события "старт" (в отличие от
            # целого турнира — TournamentService.start_tournament) — как
            # только по этой серии записана хотя бы одна игра, дальше
            # создавать новые драфты нечестно (часть результатов уже
            # известна). Существующие открытые драфты в этот момент уже
            # заблокированы отдельно — см. games.py::_lock_series_fantasy_if_needed.
            if series.stage and series.stage.games:
                return FantasyResult.fail(
                    "По этой серии уже записаны игры — драфт больше нельзя создать."
                )

        # Anti-abuse: one draft per (tournament, series, is_practice) per
        # user — a paid and a practice draft for the same tournament/series
        # can coexist (see model's unique constraint).
        existing = db.session.query(FantasyDraft).filter_by(
            user_id=user.id, tournament_id=tournament_id,
            tournament_series_id=tournament_series_id, is_practice=is_practice,
        ).first()
        if existing:
            return FantasyResult.fail(
                "У вас уже есть тренировочный драфт для этой серии." if (series and is_practice)
                else "У вас уже есть драфт для этой серии." if series
                else "У вас уже есть тренировочный драфт для этого турнира." if is_practice
                else "У вас уже есть драфт для этого турнира."
            )

        # Anti-abuse: cannot draft an evening/tournament you're playing in
        # yourself. For a series draft with a confirmed roster (see
        # series_tournaments.py::set_series_roster), this must check THAT
        # roster, not the whole tournament's — otherwise a season/tournament
        # participant who simply isn't playing THIS particular evening
        # would be wrongly blocked from drafting it (see get_available_picks,
        # which already narrows the same way). No confirmed roster set ->
        # fall back to the whole tournament's participants, same as before.
        if user.player_id:
            if series and series.confirmed_player_ids is not None:
                is_participant = user.player_id in series.confirmed_player_ids
            else:
                is_participant = db.session.query(TournamentParticipant).filter_by(
                    tournament_id=tournament_id, player_id=user.player_id
                ).first() is not None
            if is_participant:
                return FantasyResult.fail(
                    "Вы не можете создать фэнтези-драфт для серии, в которой играете сами."
                    if series else
                    "Вы не можете создать фэнтези-драфт для турнира, "
                    "в котором участвуете как игрок."
                )

        # Entry fee requires a linked player (coin balance lives on Player);
        # practice drafts are free, so skip both the balance check and the
        # actual charge entirely.
        if not user.is_player or not user.player:
            return FantasyResult.fail(
                "Для участия в Fantasy нужен привязанный профиль игрока."
            )

        label = f"{t.name} — {series.name}" if series else t.name
        entry_cost = 0.0
        if not is_practice:
            entry_cost = EconomyService.get_settings().fantasy_entry_cost
            spend = EconomyService.spend_coins(
                user.player,
                entry_cost,
                f"Fantasy: вступительный взнос «{label}»",
                commit=False,
            )
            if not spend.ok:
                return FantasyResult.fail(spend.message)

        group_number = FantasyService._assign_group(series, is_practice=is_practice) if series else None

        draft = FantasyDraft(
            user_id=user.id,
            tournament_id=tournament_id,
            tournament_series_id=tournament_series_id,
            status=FantasyDraftStatus.OPEN,
            entry_cost_paid=entry_cost,
            group_number=group_number,
            is_practice=is_practice,
        )
        db.session.add(draft)
        db.session.commit()
        group_note = f" Группа {group_number}." if group_number else ""
        if is_practice:
            return FantasyResult.success(
                f"Тренировочный драфт для «{label}» создан — бесплатно, без права на приз.{group_note} Выберите игроков.",
                data=draft,
            )
        return FantasyResult.success(
            f"Драфт для «{label}» создан, списано {entry_cost:.0f} монет.{group_note} Выберите игроков.",
            data=draft,
        )

    @staticmethod
    def _assign_group(series: TournamentSeries, is_practice: bool = False) -> int:
        """
        Группа эксклюзивности пиков внутри серии — фиксированного размера
        (SERIES_GROUP_SIZE драфтеров по SERIES_PICKS_PER_DRAFTER пиков
        каждый), заполняются по порядку присоединения; следующая
        открывается, когда текущая набрала SERIES_GROUP_SIZE драфтов.
        Уже назначенные драфты никогда не переезжают в другую группу
        задним числом, даже если позже открылась более свободная.

        Считается ОТДЕЛЬНО для платных и тренировочных (is_practice)
        драфтов — у них разная нумерация групп 1,2,3.., не пересекаются.
        """
        counts = dict(
            db.session.query(FantasyDraft.group_number, func.count(FantasyDraft.id))
            .filter(
                FantasyDraft.tournament_series_id == series.id,
                FantasyDraft.is_practice == is_practice,
                FantasyDraft.group_number.isnot(None),
            )
            .group_by(FantasyDraft.group_number)
            .all()
        )
        group = 1
        while counts.get(group, 0) >= SERIES_GROUP_SIZE:
            group += 1
        return group

    @staticmethod
    def _self_heal_series(tournament_series_id: int) -> None:
        """
        Defensive re-check, run ONCE per series on every read/edit that
        touches it: re-derives LOCKED status and live total_points for
        ALL of the series' drafts from its current games/rating, instead
        of trusting stored values blindly.

        Both the lock (lock_drafts_for_series) and the live points update
        (update_live_points_for_series) normally fire as a side effect of
        creating/attaching a game to the series' stage — see
        games.py::_lock_series_fantasy_if_needed and
        orchestrator.py::_update_fantasy_live_points. A draft that existed
        in the narrow gap before either of those hooks was deployed (or
        simply the last draft of an evening, after which no further game
        triggers a recompute) would otherwise stay OPEN and/or stuck at
        stale points until some unrelated future game happens to fire the
        hook again.

        Batched by series (not called per-draft) — an earlier per-draft
        version called update_live_points_for_series() once per OPEN/LOCKED
        draft, and that function itself recomputes EVERY such draft in the
        series, so a series with K non-scored drafts did O(K^2) recompute
        work (plus a commit per draft) on every leaderboard render.
        """
        series = db.session.get(TournamentSeries, tournament_series_id)
        if not (series and series.stage and series.stage.games):
            return
        open_drafts = db.session.query(FantasyDraft).filter_by(
            tournament_series_id=tournament_series_id, status=FantasyDraftStatus.OPEN,
        ).all()
        for d in open_drafts:
            d.status = FantasyDraftStatus.LOCKED
        FantasyService.update_live_points_for_series(tournament_series_id, commit=False)
        db.session.commit()

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
        if draft.tournament_series_id:
            FantasyService._self_heal_series(draft.tournament_series_id)
        if draft.status != FantasyDraftStatus.OPEN:
            return FantasyResult.fail("Драфт зафиксирован — изменения невозможны.")

        # Pick limit
        participant_count = db.session.query(TournamentParticipant).filter_by(
            tournament_id=draft.tournament_id
        ).count()
        max_picks = _allowed_picks(participant_count, is_series=bool(draft.tournament_series_id))
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

        # Эксклюзивность — только для серийных драфтов, только внутри своей
        # группы (см. _assign_group): тот же игрок не может быть выбран
        # ДРУГИМ драфтом этой же (серия, группа), но свободно доступен
        # драфтерам из другой группы той же серии.
        if draft.tournament_series_id and draft.group_number:
            taken_elsewhere = (
                db.session.query(FantasyDraftPick)
                .join(FantasyDraft, FantasyDraft.id == FantasyDraftPick.draft_id)
                .filter(
                    FantasyDraft.tournament_series_id == draft.tournament_series_id,
                    FantasyDraft.group_number == draft.group_number,
                    FantasyDraft.is_practice == draft.is_practice,
                    FantasyDraft.id != draft.id,
                    FantasyDraftPick.player_id == player_id,
                )
                .first()
            )
            if taken_elsewhere:
                return FantasyResult.fail(
                    f"«{player.display_name}» уже выбран другим менеджером в вашей группе."
                )

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
        if draft.tournament_series_id:
            FantasyService._self_heal_series(draft.tournament_series_id)
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
    def cancel_draft(user: User, draft_id: int) -> FantasyResult:
        """
        Fully withdraw an OPEN draft: refunds the entry fee and deletes the
        draft (picks cascade). Only OPEN drafts can be cancelled — once
        locked, the evening/tournament may already be underway, so pulling
        out isn't fair to the rest of the pool. For series drafts, this
        also frees the drafter's spot in their exclusivity group for the
        next person to join (group_number isn't reassigned to anyone else
        retroactively — see _assign_group — the slot just becomes free).
        """
        from app.services.economy_service import EconomyService

        draft = db.session.get(FantasyDraft, draft_id)
        if not draft or (draft.user_id != user.id and not user.is_admin):
            return FantasyResult.fail("Доступ запрещён.")
        if draft.tournament_series_id:
            FantasyService._self_heal_series(draft.tournament_series_id)
        if draft.status != FantasyDraftStatus.OPEN:
            return FantasyResult.fail("Драфт уже зафиксирован — отменить нельзя.")

        owner = draft.user
        refund = draft.entry_cost_paid
        tournament_id = draft.tournament_id
        tournament_series_id = draft.tournament_series_id
        was_practice = draft.is_practice

        db.session.delete(draft)
        if refund > 0 and owner and owner.player:
            EconomyService.add_coins(
                owner.player,
                refund,
                "Fantasy: возврат взноса за отменённый драфт",
                CoinSourceType.FANTASY_REWARD,
                ref_tournament_id=tournament_id,
                commit=False,
            )
        db.session.commit()
        message = (
            "Тренировочный драфт отменён." if was_practice
            else f"Драфт отменён, возвращено {refund:.0f} монет."
        )
        return FantasyResult.success(
            message,
            data={"tournament_id": tournament_id, "tournament_series_id": tournament_series_id},
        )

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

    @staticmethod
    def lock_drafts_for_series(tournament_series_id: int, commit: bool = True) -> int:
        """
        Lock all OPEN drafts scoped to one series. Series-tournaments never
        transition through Tournament.status "active" (they stay "pending"
        for their whole lifecycle — see SeriesTournamentService), so
        lock_drafts_for_tournament never fires for them; this is the
        series-scoped equivalent, called from finish_series() right before
        scoring.
        """
        drafts = db.session.query(FantasyDraft).filter_by(
            tournament_series_id=tournament_series_id,
            status=FantasyDraftStatus.OPEN,
        ).all()
        for d in drafts:
            d.status = FantasyDraftStatus.LOCKED
        if commit:
            db.session.commit()
        logger.info(f"Locked {len(drafts)} fantasy drafts for series #{tournament_series_id}")
        return len(drafts)

    # ── Live points (preview, not final) ────────────────────────────────────
    #
    # total_points used to sit at 0 for the whole evening/tournament until
    # an admin explicitly finished it and score_series()/score_tournament()
    # ran — confusing, since the underlying games are already finished and
    # scored individually. These two recompute total_points from the
    # CURRENT rating after every game, so standings update live, without
    # touching draft.status or paying out the prize pool — that stays a
    # deliberate one-time action tied to actually finishing the series/
    # tournament (score_series/score_tournament, called from
    # finish_series()/finish_tournament()), which also marks drafts SCORED
    # and is guarded against re-running. Safe to call repeatedly.

    @staticmethod
    def update_live_points_for_series(tournament_series_id: int, commit: bool = True) -> None:
        from app.services.rating_service import RatingService

        series = db.session.get(TournamentSeries, tournament_series_id)
        if not series:
            return
        drafts = (
            db.session.query(FantasyDraft)
            .filter(
                FantasyDraft.tournament_series_id == tournament_series_id,
                FantasyDraft.status != FantasyDraftStatus.SCORED,
            )
            .all()
        )
        if not drafts:
            return
        ratings = RatingService.get_stage_rating(series.stage_id)
        points_map = {r.player_id: r.total_score for r in ratings}
        for draft in drafts:
            total = 0.0
            for pick in draft.picks:
                pts = points_map.get(pick.player_id, 0.0)
                pick.points_earned = round(pts, 2)
                total += pts
            draft.total_points = round(total, 2)
        if commit:
            db.session.commit()

    @staticmethod
    def update_live_points_for_tournament(tournament_id: int, commit: bool = True) -> None:
        from app.services.rating_service import RatingService

        drafts = (
            db.session.query(FantasyDraft)
            .filter(
                FantasyDraft.tournament_id == tournament_id,
                FantasyDraft.tournament_series_id.is_(None),
                FantasyDraft.status != FantasyDraftStatus.SCORED,
            )
            .all()
        )
        if not drafts:
            return
        ratings = RatingService.get_tournament_rating(tournament_id)
        points_map = {r.player_id: r.total_score for r in ratings}
        for draft in drafts:
            total = 0.0
            for pick in draft.picks:
                pts = points_map.get(pick.player_id, 0.0)
                pick.points_earned = round(pts, 2)
                total += pts
            draft.total_points = round(total, 2)
        if commit:
            db.session.commit()

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
            tournament_id=tournament_id, tournament_series_id=None,
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

        # ── Prize pool payout — paid drafts only. Practice drafts (see
        # module docstring) are scored above like any other draft, but
        # must never be able to rank into a payout slot, so the bank and
        # leaderboard here are both explicitly restricted to is_practice=False.
        paid_drafts = [d for d in all_drafts if not d.is_practice]
        bank = round(sum(d.entry_cost_paid for d in paid_drafts), 2)
        if bank > 0:
            settings = EconomyService.get_settings()
            leaderboard = FantasyService.get_leaderboard(tournament_id, is_practice=False)
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
    def score_series(tournament_series_id: int, commit: bool = True) -> List[FantasyResult]:
        """
        Series-scoped equivalent of score_tournament — points come from
        RatingService.get_stage_rating(series.stage_id) (just that one
        evening) instead of the whole-tournament rating, and the prize
        pool is the bank of only THIS series' drafts. Called from
        SeriesTournamentService.finish_series() right after
        lock_drafts_for_series().
        """
        from app.services.rating_service import RatingService
        from app.services.economy_service import EconomyService

        series = db.session.get(TournamentSeries, tournament_series_id)
        if not series or series.status != SeriesStatus.FINISHED:
            return [FantasyResult.fail("Серия не завершена.")]

        t = series.series_tournament.tournament
        all_drafts = db.session.query(FantasyDraft).filter_by(
            tournament_series_id=tournament_series_id,
        ).all()
        if not all_drafts:
            return [FantasyResult.fail("Нет Fantasy-драфтов для этой серии.")]

        unscored = [d for d in all_drafts if d.status != FantasyDraftStatus.SCORED]
        if not unscored:
            return [FantasyResult.fail("Все драфты этой серии уже подсчитаны.")]

        ratings = RatingService.get_stage_rating(series.stage_id)
        points_map = {r.player_id: r.total_score for r in ratings}

        label = f"{t.name} — {series.name}"
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
                    {"tournament_name": label, "points": draft.total_points},
                )

        # ── Prize pool payout — one bank + one leaderboard PER EXCLUSIVITY
        # GROUP, not one for the whole series (see _assign_group — groups
        # share the same small confirmed-roster pool, so each is its own
        # self-contained mini-competition with its own entry fees/payout).
        # group_number is None for drafts created before this feature
        # shipped — treated as a single implicit group, same as the old
        # whole-series behavior. Practice drafts (see module docstring) are
        # excluded entirely here — group numbering is scoped separately per
        # is_practice (see _assign_group), so filtering paid_drafts also
        # keeps a practice group's group_number from colliding with a paid
        # one of the same number.
        settings = EconomyService.get_settings()
        paid_drafts = [d for d in all_drafts if not d.is_practice]
        groups = sorted({d.group_number for d in paid_drafts}, key=lambda g: (g is None, g))
        for group_number in groups:
            group_drafts = [d for d in paid_drafts if d.group_number == group_number]
            bank = round(sum(d.entry_cost_paid for d in group_drafts), 2)
            if bank <= 0:
                continue
            leaderboard = FantasyService.get_leaderboard(
                t.id, tournament_series_id, group_number=group_number, is_practice=False,
            )
            group_label = f"{label} (группа {group_number})" if group_number else label
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
                    f"Fantasy место #{place} в «{group_label}» (банк {bank:.0f})",
                    CoinSourceType.FANTASY_REWARD,
                    ref_tournament_id=t.id,
                    commit=False,
                )
                BotNotifyService.notify_player(
                    user.player.id, "fantasy-prize",
                    {"tournament_name": group_label, "place": place, "amount": amount},
                )
        if commit:
            db.session.commit()

        return results

    @staticmethod
    def get_pool_info(
        tournament_id: int, tournament_series_id: Optional[int] = None,
        group_number: Optional[int] = None, is_practice: bool = False,
    ) -> dict:
        """
        Entry cost, participant count, current bank and projected payouts
        for the tournament's (or one series', or one exclusivity group
        within a series') Fantasy page. Bank is the sum of what was
        actually charged to each draft (entry_cost_paid), so it stays
        correct even if the admin changes the entry cost mid-way.

        is_practice=True always returns entry_cost/bank/payouts of 0 —
        practice drafts never charge or pay out (see module docstring);
        participant_count is still meaningful (how many are training).
        """
        from app.services.economy_service import EconomyService

        settings = EconomyService.get_settings()
        query = db.session.query(FantasyDraft).filter_by(
            tournament_id=tournament_id, tournament_series_id=tournament_series_id,
            is_practice=is_practice,
        )
        if group_number is not None:
            query = query.filter(FantasyDraft.group_number == group_number)
        drafts = query.all()

        bank = round(sum(d.entry_cost_paid for d in drafts), 2)
        return {
            "entry_cost": 0 if is_practice else settings.fantasy_entry_cost,
            "participant_count": len(drafts),
            "bank": bank,
            "payout_1st": round(bank * settings.fantasy_first_place_share, 2),
            "payout_2nd": round(bank * settings.fantasy_second_place_share, 2),
        }

    # ── Leaderboard ───────────────────────────────────────────────────────────

    @staticmethod
    def get_leaderboard(
        tournament_id: int, tournament_series_id: Optional[int] = None,
        group_number: Optional[int] = None, is_practice: bool = False,
    ) -> List[FantasyLeaderboardEntry]:
        """
        group_number=None (default) with a series that DOES use exclusivity
        groups returns the combined list across all groups, each entry
        tagged with its own group_number (see FantasyLeaderboardEntry) —
        callers that need one group's standalone ranking/payout (score_series)
        pass group_number explicitly.

        is_practice filters to just paid (False, default) or just practice
        (True) drafts — the two are always separate leaderboards, never
        mixed (a practice draft must never be able to rank into a paid
        payout slot, see score_tournament/score_series).
        """
        # Self-heal BEFORE the query, once for the whole series — not per
        # draft in the loop below, and not after ORDER BY has already run
        # (both of which the older version did, so the rank order could
        # reflect stale total_points on the very render that fixes them).
        if tournament_series_id:
            FantasyService._self_heal_series(tournament_series_id)

        query = db.session.query(FantasyDraft).filter_by(
            tournament_id=tournament_id, tournament_series_id=tournament_series_id,
            is_practice=is_practice,
        )
        if group_number is not None:
            query = query.filter(FantasyDraft.group_number == group_number)
        drafts = query.order_by(FantasyDraft.total_points.desc()).all()

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
                group_number=d.group_number,
                status=d.status.value,
                picks=[
                    {
                        "player_id": p.player_id,
                        "player": p.player,
                        "display_name": p.player.display_name if p.player else "?",
                        "points_earned": p.points_earned,
                    }
                    for p in d.picks
                ],
            ))
        return entries

    @staticmethod
    def get_user_draft(
        user_id: int, tournament_id: int, tournament_series_id: Optional[int] = None,
        is_practice: bool = False,
    ) -> Optional[FantasyDraft]:
        if tournament_series_id:
            FantasyService._self_heal_series(tournament_series_id)
        return db.session.query(FantasyDraft).filter_by(
            user_id=user_id, tournament_id=tournament_id,
            tournament_series_id=tournament_series_id, is_practice=is_practice,
        ).first()

    @staticmethod
    def get_top_picks(
        tournament_id: int, tournament_series_id: Optional[int] = None, limit: int = 3,
    ) -> List[dict]:
        """Самые популярные пики (по числу драфтов, выбравших игрока) для
        карточки турнира/серии — одна GROUP BY на количество драфтов этого
        турнира (обычно единицы-десятки), не итерация по игрокам/играм."""
        rows = (
            db.session.query(FantasyDraftPick.player_id, func.count(FantasyDraftPick.id))
            .join(FantasyDraft, FantasyDraft.id == FantasyDraftPick.draft_id)
            .filter(
                FantasyDraft.tournament_id == tournament_id,
                FantasyDraft.tournament_series_id == tournament_series_id,
            )
            .group_by(FantasyDraftPick.player_id)
            .order_by(func.count(FantasyDraftPick.id).desc())
            .limit(limit)
            .all()
        )
        if not rows:
            return []
        players = {
            p.id: p for p in db.session.query(Player).filter(
                Player.id.in_([pid for pid, _ in rows])
            ).all()
        }
        return [
            {"player": players.get(pid), "pick_count": cnt}
            for pid, cnt in rows if players.get(pid)
        ]

    @staticmethod
    def get_global_stats() -> dict:
        """Сайтовая витрина Fantasy — суммарный банк и число участников за
        всё время + сколько турниров/серий сейчас активны. Три дешёвых
        агрегата, считаются один раз на загрузку главной страницы Fantasy
        (не в цикле по турнирам)."""
        total_bank = round(
            db.session.query(func.sum(FantasyDraft.entry_cost_paid)).scalar() or 0.0, 2
        )
        total_participants = db.session.query(
            func.count(func.distinct(FantasyDraft.user_id))
        ).scalar() or 0
        active_series_count = db.session.query(TournamentSeries).filter_by(
            status=SeriesStatus.ACTIVE
        ).count()
        active_tournaments_count = db.session.query(Tournament).filter(
            Tournament.status.in_(["pending", "active"])
        ).count()
        return {
            "total_bank": total_bank,
            "total_participants": total_participants,
            "active_count": active_series_count + active_tournaments_count,
        }

    @staticmethod
    def get_available_picks(
        user: User, tournament_id: int, tournament_series_id: Optional[int] = None,
        is_practice: bool = False,
    ) -> List[Player]:
        """
        Players available for the user to pick — in tournament, not self,
        not already picked in THIS draft.

        Default eligibility pool is the whole tournament's participants
        (same players are draftable for any individual series/evening, not
        just those who already have results recorded for that specific
        evening — drafting happens before the evening is played).

        If the series has a confirmed roster set (TournamentSeries.
        confirmed_player_ids — an admin explicitly declared who's actually
        playing that evening, see series_tournaments.py::set_series_roster),
        narrow the pool to just those players instead — drafting a player
        who isn't even at the table tonight would score zero anyway, so
        this just keeps the picker honest about who can realistically earn
        points.

        If the draft belongs to an exclusivity group (series-scoped, see
        _assign_group), also excludes players already picked by ANY OTHER
        draft in that same (series, group, is_practice) — not just this
        user's own draft. is_practice selects which of the user's two
        possible drafts (paid vs. practice) this is about.
        """
        draft = FantasyService.get_user_draft(user.id, tournament_id, tournament_series_id, is_practice=is_practice)
        already_picked = {p.player_id for p in draft.picks} if draft else set()

        confirmed_ids = None
        if tournament_series_id:
            series = db.session.get(TournamentSeries, tournament_series_id)
            confirmed_ids = series.confirmed_player_ids if series else None

        taken_by_group = set()
        if draft and draft.tournament_series_id and draft.group_number:
            rows = (
                db.session.query(FantasyDraftPick.player_id)
                .join(FantasyDraft, FantasyDraft.id == FantasyDraftPick.draft_id)
                .filter(
                    FantasyDraft.tournament_series_id == draft.tournament_series_id,
                    FantasyDraft.group_number == draft.group_number,
                    FantasyDraft.is_practice == draft.is_practice,
                    FantasyDraft.id != draft.id,
                )
                .all()
            )
            taken_by_group = {pid for (pid,) in rows}

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
            if p.player_id in taken_by_group:
                continue                    # exclusively picked by a group-mate
            if confirmed_ids is not None and p.player_id not in confirmed_ids:
                continue                    # not confirmed for this evening
            if p.player and p.player.is_active:
                result.append(p.player)
        return sorted(result, key=lambda pl: pl.display_name)
