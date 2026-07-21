"""
EloEngine
=========
Match-level rating engine. Computes per-player ELO deltas using:

    Δμᵢ = α · (Rᵢ − Eᵢ) · kᵢ · uᵢ
        + α · sᵢ · K
        + λ · bᵢ

Where:
    Rᵢ  — actual result (win/loss + contribution component)
    Eᵢ  — expected result (logistic function of average team ELO gap)
    kᵢ  — role multiplier (Sheriff/Don carry more signal than rank-and-file)
    uᵢ  — uncertainty factor (new players move faster, "placement matches")
    sᵢ  — quality score in [-1, +1], admin/judge assessed performance
    K   — quality weight (global constant)
    bᵢ  — special event bonus (PU — "поднятая рука" / standout play)
    α   — global learning rate
    λ   — special event weight

Design rules:
    - Deterministic: same inputs → same output, always. No randomness.
    - Pure functions wherever possible — easy to unit test in isolation.
    - ELO is LONG-TERM ranking. It must NOT be influenced by season-only
      bonuses (GG). Those live exclusively in SeasonRatingEngine.
    - No Flask imports. No direct DB writes inside pure-math functions —
      only the top-level apply_match() touches the session.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Sequence

from sqlalchemy import or_, and_

from app import db
from app.models import Game, GameSlot, Player, Role, WinSide

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Global tunable constants
# ---------------------------------------------------------------------------

ALPHA = 1.0        # global learning rate applied to (R-E) and quality terms
LAMBDA = 0.5        # weight of special-event bonus (b_i)
QUALITY_WEIGHT_K = 6.0   # K: how many ELO points a full +1.0 quality swing is worth
BASE_K_FACTOR = 32.0     # base k_i before role/uncertainty adjustments

# Role multipliers — Sheriff/Don decisions carry more signal (higher variance, higher skill ceiling)
ROLE_MULTIPLIERS: dict[Role, float] = {
    Role.SHERIFF:  1.25,
    Role.DON:      1.20,
    Role.MAFIA:    1.05,
    Role.CIVILIAN: 1.00,
}

# Uncertainty (u_i): new players have higher uncertainty → faster convergence
PLACEMENT_MATCHES = 15      # below this games count, uncertainty boost applies
PLACEMENT_UNCERTAINTY = 1.6  # multiplier during placement
VETERAN_GAMES_THRESHOLD_1 = 50
VETERAN_GAMES_THRESHOLD_2 = 100
VETERAN_DAMPENING_1 = 0.85
VETERAN_DAMPENING_2 = 0.65

# PU event bonus per occurrence (b_i contribution unit)
PU_BONUS_PER_EVENT = 4.0
PU_BONUS_CAP = 20.0   # cap total b_i contribution per slot — anti-abuse


# ---------------------------------------------------------------------------
# Per-player computation inputs/outputs (pure dataclasses, no DB coupling)
# ---------------------------------------------------------------------------

@dataclass
class EloInputs:
    """Everything EloEngine needs for one player's delta — no ORM objects."""
    player_id: int
    current_elo: float
    games_played: int
    role: Role
    won: bool
    team_avg_elo: float
    opponent_avg_elo: float
    quality_score: float | None   # s_i, may be None → treated as 0
    pu_count: int                 # raw special-event count this match


@dataclass
class EloDelta:
    player_id: int
    delta: float
    expected: float
    actual_component: float
    quality_component: float
    event_component: float
    new_elo: float

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "delta": round(self.delta, 3),
            "expected": round(self.expected, 4),
            "actual_component": round(self.actual_component, 3),
            "quality_component": round(self.quality_component, 3),
            "event_component": round(self.event_component, 3),
            "new_elo": round(self.new_elo, 2),
        }


class EloEngine:
    """
    Stateless engine — every method is deterministic given its inputs.
    The orchestration (DB reads/writes) lives in apply_match(); everything
    else is pure and independently testable.
    """

    # ── Expected result Eᵢ ────────────────────────────────────────────────────

    @staticmethod
    def compute_expected_result(team_avg_elo: float, opponent_avg_elo: float) -> float:
        """
        Standard logistic expectation, same shape as classic ELO.
        Returns value in (0, 1).
        """
        return 1.0 / (1.0 + 10 ** ((opponent_avg_elo - team_avg_elo) / 400.0))

    # ── Role multiplier kᵢ ────────────────────────────────────────────────────

    @staticmethod
    def apply_role_multiplier(role: Role) -> float:
        return ROLE_MULTIPLIERS.get(role, 1.0)

    # ── Uncertainty uᵢ ────────────────────────────────────────────────────────

    @staticmethod
    def apply_uncertainty(games_played: int) -> float:
        """
        New players (placement matches) move faster toward their true rating.
        Veterans are dampened to resist long-run inflation/abuse.
        """
        if games_played < PLACEMENT_MATCHES:
            return PLACEMENT_UNCERTAINTY
        if games_played > VETERAN_GAMES_THRESHOLD_2:
            return VETERAN_DAMPENING_2
        if games_played > VETERAN_GAMES_THRESHOLD_1:
            return VETERAN_DAMPENING_1
        return 1.0

    # ── Special event bonus bᵢ ────────────────────────────────────────────────

    @staticmethod
    def apply_special_events(pu_count: int) -> float:
        """
        b_i — bounded, deterministic. Capped to prevent single-match abuse
        (e.g. judge spamming PU flags to inflate one player's ELO).
        """
        raw = max(0, pu_count) * PU_BONUS_PER_EVENT
        return min(raw, PU_BONUS_CAP)

    # ── Actual result Rᵢ (win/loss + contribution) ───────────────────────────

    @staticmethod
    def compute_actual_result(won: bool, quality_score: float | None) -> float:
        """
        R_i blends binary outcome with a small contribution nudge so that
        a strong loss isn't scored identically to a passive loss.
        Quality contributes at most ±0.1 to keep win/loss dominant.
        """
        base = 1.0 if won else 0.0
        contribution_nudge = (quality_score or 0.0) * 0.1
        return max(0.0, min(1.0, base + contribution_nudge))

    # ── Full per-player delta ─────────────────────────────────────────────────

    @staticmethod
    def compute_match_delta(inputs: EloInputs) -> EloDelta:
        """
        Δμᵢ = α·(Rᵢ−Eᵢ)·kᵢ·uᵢ  +  α·sᵢ·K  +  λ·bᵢ
        """
        e_i = EloEngine.compute_expected_result(
            inputs.team_avg_elo, inputs.opponent_avg_elo
        )
        r_i = EloEngine.compute_actual_result(inputs.won, inputs.quality_score)
        k_i = EloEngine.apply_role_multiplier(inputs.role)
        u_i = EloEngine.apply_uncertainty(inputs.games_played)
        s_i = inputs.quality_score or 0.0
        b_i = EloEngine.apply_special_events(inputs.pu_count)

        actual_component    = ALPHA * (r_i - e_i) * BASE_K_FACTOR * k_i * u_i
        quality_component   = ALPHA * s_i * QUALITY_WEIGHT_K
        event_component     = LAMBDA * b_i

        delta = actual_component + quality_component + event_component
        new_elo = round(inputs.current_elo + delta, 2)

        return EloDelta(
            player_id=inputs.player_id,
            delta=delta,
            expected=e_i,
            actual_component=actual_component,
            quality_component=quality_component,
            event_component=event_component,
            new_elo=new_elo,
        )

    # ── Orchestration: apply to a finished Game ──────────────────────────────

    @staticmethod
    def apply_match(game: Game, commit: bool = True) -> List[EloDelta]:
        """
        Compute and persist ELO deltas for every slot in a finished, ranked game.
        Deterministic: re-running on the same game state produces the same
        deltas (idempotency is the CALLER's responsibility — this does not
        check "have we already applied ELO for this game", because that
        bookkeeping belongs to the orchestrator / a processed_at flag).
        """
        if not game.is_finished or game.win_side == WinSide.NONE:
            return []

        slots = game.slots
        mafia_slots = [s for s in slots if s.is_mafia_side]
        city_slots  = [s for s in slots if s.is_city_side]

        def avg_elo(slot_list: Sequence[GameSlot]) -> float:
            elos = [s.player.elo for s in slot_list if s.player]
            return sum(elos) / len(elos) if elos else 1000.0

        def games_played_as_of(player_id: int) -> int:
            """
            Chronologically-scoped count (inclusive of THIS game) — not a
            live .count() of all of the player's slots, which returns their
            CURRENT career total regardless of replay position. That's
            harmless when apply_match runs live right after a new game
            (no future games exist yet, so the count IS correct as-of-now),
            but silently corrupts placement/veteran dampening during any
            bulk replay (recompute_chain_from, recompute_all_elo.py) —
            every future game already exists in the DB by the time those
            run, so even a player's very first replayed game would see
            their FINAL career count instead of 1.
            """
            return (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == player_id,
                    Game.is_finished == True,
                    Game.is_ranked == True,
                    or_(
                        Game.played_at < game.played_at,
                        and_(Game.played_at == game.played_at, Game.id <= game.id),
                    ),
                )
                .count()
            )

        mafia_avg = avg_elo(mafia_slots)
        city_avg  = avg_elo(city_slots)
        mafia_won = game.win_side == WinSide.MAFIA

        deltas: List[EloDelta] = []

        # PU event → extra pu_count unit for ELO b_i term.
        # Successful PU (≥2 mafia) counts as a standout event.
        def effective_pu_count(slot) -> int:
            base = getattr(slot, "pu_count", 0) or 0
            is_pu = getattr(slot, "is_pu", False)
            pu_mafia = getattr(slot, "pu_mafia_count", 0) or 0
            if is_pu and pu_mafia >= 2:
                base += 1   # successful PU prediction adds one standout unit
            return base

        for slot in mafia_slots:
            if not slot.player:
                continue
            inputs = EloInputs(
                player_id=slot.player_id,
                current_elo=slot.player.elo,
                games_played=games_played_as_of(slot.player_id),
                role=slot.role,
                won=mafia_won,
                team_avg_elo=mafia_avg,
                opponent_avg_elo=city_avg,
                quality_score=getattr(slot, "quality_score", None),
                pu_count=effective_pu_count(slot),
            )
            d = EloEngine.compute_match_delta(inputs)
            slot.player.elo = d.new_elo
            slot.elo_after = d.new_elo  # снимок для графика истории ELO
            db.session.add(slot.player)
            deltas.append(d)

        for slot in city_slots:
            if not slot.player:
                continue
            inputs = EloInputs(
                player_id=slot.player_id,
                current_elo=slot.player.elo,
                games_played=games_played_as_of(slot.player_id),
                role=slot.role,
                won=(not mafia_won),
                team_avg_elo=city_avg,
                opponent_avg_elo=mafia_avg,
                quality_score=getattr(slot, "quality_score", None),
                pu_count=effective_pu_count(slot),
            )
            d = EloEngine.compute_match_delta(inputs)
            slot.player.elo = d.new_elo
            slot.elo_after = d.new_elo  # снимок для графика истории ELO
            db.session.add(slot.player)
            deltas.append(d)

        if commit:
            db.session.commit()

        logger.info(
            f"EloEngine: applied {len(deltas)} deltas for game #{game.id}"
        )
        return deltas

    # ── Chain recompute: editing an already-finished game ────────────────────

    @staticmethod
    def recompute_chain_from(
        anchor_game: Game, extra_player_ids: Sequence[int] = (), commit: bool = True,
    ) -> int:
        """
        ELO is a running total on Player.elo, not a per-game-reversible
        value — apply_match() always reads whatever elo is CURRENTLY on
        the player. So correcting one historical game means: reset every
        touched player back to their value right before this game, then
        replay every ranked/finished game from this game onward, in
        chronological order, so later games naturally cascade off the
        corrected earlier ones exactly as they originally did.

        extra_player_ids: players who were in the OLD version of
        anchor_game's slots but got removed by the edit (seat reassigned
        to someone else) — they must still be reset even though no game
        from this point on references them anymore (that reset to their
        pre-cutoff baseline IS the fully-corrected final value for them).

        Returns the number of games replayed.
        """
        cutoff_at = anchor_game.played_at
        cutoff_id = anchor_game.id

        games_to_replay = (
            db.session.query(Game)
            .filter(
                Game.is_finished == True,
                Game.is_ranked == True,
                or_(
                    Game.played_at > cutoff_at,
                    and_(Game.played_at == cutoff_at, Game.id >= cutoff_id),
                ),
            )
            .order_by(Game.played_at.asc(), Game.id.asc())
            .all()
        )

        player_ids = set(extra_player_ids)
        for g in games_to_replay:
            player_ids.update(s.player_id for s in g.slots)

        for pid in player_ids:
            player = db.session.get(Player, pid)
            if not player:
                continue
            prior_slot = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == pid,
                    Game.is_finished == True,
                    Game.is_ranked == True,
                    or_(
                        Game.played_at < cutoff_at,
                        and_(Game.played_at == cutoff_at, Game.id < cutoff_id),
                    ),
                )
                .order_by(Game.played_at.desc(), Game.id.desc())
                .first()
            )
            player.elo = (
                prior_slot.elo_after
                if prior_slot and prior_slot.elo_after is not None
                else 1000.0
            )
            db.session.add(player)
        db.session.flush()

        for g in games_to_replay:
            EloEngine.apply_match(g, commit=False)

        if commit:
            db.session.commit()

        logger.info(
            f"EloEngine: recomputed chain from game #{anchor_game.id} — "
            f"{len(games_to_replay)} games replayed, {len(player_ids)} players reset"
        )
        return len(games_to_replay)
