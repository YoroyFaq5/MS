"""
SeasonRatingEngine
===================
Aggregate, season-scoped rating. Completely independent from ELO.

    SeasonRating = (TotalPoints * WR%) + (GG * gg_weight)

Where:
    TotalPoints — sum of GameSlot.total_score (base + bonus) within the season
    WR%         — wins / games_played for that season (0..1)
    GG          — sum of active GG bonuses for that player in that season
                  (GGService.get_player_season_gg_total — strictly season-scoped)
    gg_weight   — Season.gg_weight, fixed on that season's row at creation
                  time (see SeasonService.ensure_year_exists). Existing
                  seasons keep 0.2 forever (see migrate_season_gg_weight.py);
                  every season created from now on gets 0.1. Never a global
                  constant applied uniformly — each season's own historical
                  result stays exactly as it was computed at the time.

Ranking rule (places 1-5):
    Only a player with at least MIN_GAMES_FOR_TOP5 (8) finished ranked games
    in this season may occupy ranks 1-5. Players below that threshold are
    still shown (never dropped from the table) but their rank starts at 6,
    ordered by season_rating same as everyone else past place 5. If fewer
    than TOP5_SLOTS (5) players qualify, the unused top slots are left
    EMPTY rather than backfilled with an ineligible player — rank 6 always
    goes to the next player in line, never rank (qualified_count + 1).
    This rule is centralized here so every consumer (season table UI, API,
    season close/tiebreak winner selection, season awards/achievements,
    "Стол года" qualification) agrees on who counts as "top 5" without
    re-implementing the games-played floor themselves.

Design rules:
    - Deterministic: same DB state → same numbers, every time (including a
      stable tiebreak order — by player_id — for equal season_rating).
    - Does NOT read or write Player.elo. ELO and SeasonRating are
      computed by separate engines and never cross-contaminate.
    - Cacheable: SeasonRatingEngine.compute_season_ratings() is a pure
      read+compute operation safe to memoize/cache by (season_id, version).
    - Supports full season recalculation and partial (single player)
      recalculation without re-touching unrelated rows.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app import db
from app.models import Player, GameSlot, Game, Season
from app.services.gg_service import GGService

# Legacy/default GG weight — used only as a fallback when a season row is
# somehow unavailable (should not happen in practice: Season.gg_weight is
# NOT NULL). This is NOT a global override of Season.gg_weight; the real
# per-season value always wins when a season row exists.
GG_WEIGHT = 0.2

# Places 1-5 of the season table are reserved for players who've actually
# played a meaningful sample this season — see module docstring.
MIN_GAMES_FOR_TOP5 = 8
TOP5_SLOTS = 5


@dataclass
class SeasonRatingEntry:
    player_id: int
    display_name: str
    games_played: int = 0
    games_won: int = 0
    win_rate: float = 0.0          # WR%  — 0..1 (not 0..100)
    total_points: float = 0.0      # sum of GameSlot.total_score this season
    gg_total: float = 0.0          # sum of active GG entries this season
    gg_weight: float = GG_WEIGHT   # this season's GG weight (informational)
    season_rating: float = 0.0     # final composite score
    elo: float = 1000.0            # current global ELO (informational — not part of the formula)
    rank: int = 0
    # True once this player has played MIN_GAMES_FOR_TOP5+ ranked games this
    # season — the only players who may occupy ranks 1..TOP5_SLOTS.
    meets_top5_min_games: bool = False
    # 0 once meets_top5_min_games is True — how many more ranked games this
    # player needs this season before they're eligible for a top-5 place.
    games_needed_for_top5: int = 0

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "player_id": self.player_id,
            "display_name": self.display_name,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate_pct": round(self.win_rate * 100, 1),
            "total_points": round(self.total_points, 2),
            "gg_total": round(self.gg_total, 2),
            "gg_weight": self.gg_weight,
            "season_rating": round(self.season_rating, 2),
            "elo": round(self.elo, 1),
            "meets_top5_min_games": self.meets_top5_min_games,
            "games_needed_for_top5": self.games_needed_for_top5,
        }


class SeasonRatingEngine:

    MIN_GAMES_FOR_TOP5 = MIN_GAMES_FOR_TOP5
    TOP5_SLOTS = TOP5_SLOTS

    # ── Core formula (pure function — easy to unit test) ──────────────────────

    @staticmethod
    def compute_season_rating(
        total_points: float, win_rate: float, gg_total: float, gg_weight: float = GG_WEIGHT
    ) -> float:
        """
        SeasonRating = (TotalPoints * WR%) + (GG * gg_weight)
        win_rate must be in [0, 1]. gg_weight defaults to the legacy 0.2
        only for callers that don't have a season row at hand — real
        callers should always pass the season's own Season.gg_weight.
        """
        return round((total_points * win_rate) + (gg_total * gg_weight), 4)

    # ── Per-player aggregate (no DB writes — pure read+compute) ──────────────

    @staticmethod
    def compute_player_entry(
        player: Player, season_id: int, season: Optional[Season] = None
    ) -> Optional[SeasonRatingEntry]:
        slots = (
            db.session.query(GameSlot)
            .join(Game)
            .filter(
                GameSlot.player_id == player.id,
                Game.is_finished == True,
                Game.is_ranked == True,
                Game.season_id == season_id,
            )
            .all()
        )
        if not slots:
            return None

        if season is None:
            season = db.session.get(Season, season_id)
        gg_weight = season.gg_weight if season is not None else GG_WEIGHT

        games_played = len(slots)
        games_won = 0
        total_points = 0.0

        for slot in slots:
            total_points += slot.total_score
            game = slot.game
            won = (
                (slot.is_mafia_side and game.win_side.value == "mafia")
                or (slot.is_city_side and game.win_side.value == "city")
            )
            if won:
                games_won += 1

        win_rate = games_won / games_played if games_played else 0.0
        gg_total = GGService.get_player_season_gg_total(player.id, season_id)

        rating = SeasonRatingEngine.compute_season_rating(
            total_points, win_rate, gg_total, gg_weight
        )

        meets_top5 = games_played >= MIN_GAMES_FOR_TOP5

        return SeasonRatingEntry(
            player_id=player.id,
            display_name=player.display_name,
            games_played=games_played,
            games_won=games_won,
            win_rate=win_rate,
            total_points=round(total_points, 2),
            gg_total=gg_total,
            gg_weight=gg_weight,
            season_rating=rating,
            elo=player.elo,
            meets_top5_min_games=meets_top5,
            games_needed_for_top5=max(0, MIN_GAMES_FOR_TOP5 - games_played),
        )

    # ── Full season recalculation ──────────────────────────────────────────────

    @staticmethod
    def compute_season_ratings(season_id: int) -> List[SeasonRatingEntry]:
        """
        Full recalculation for every player who played a ranked game
        in this season. Stateless — does not write anything to the DB;
        callers decide whether/how to persist or cache the result.

        Ordering/ranking (see module docstring for the full rule):
        players with >= MIN_GAMES_FOR_TOP5 games are ranked by season_rating
        (ties broken by player_id for determinism) and take ranks 1..N
        (N = min(TOP5_SLOTS, count of eligible players) — unused top slots
        are left empty, never backfilled). Every remaining player (both the
        eligible overflow past TOP5_SLOTS and everyone below the games
        floor) is ranked by season_rating starting at rank TOP5_SLOTS + 1,
        regardless of how many top slots were actually filled.
        """
        season = db.session.get(Season, season_id)
        if not season:
            return []

        # Only players who have at least one slot in this season are relevant —
        # avoids scanning all 10k+ players when only a few hundred played.
        player_ids = (
            db.session.query(GameSlot.player_id)
            .join(Game)
            .filter(Game.season_id == season_id, Game.is_finished == True, Game.is_ranked == True)
            .distinct()
            .all()
        )
        player_ids = [pid for (pid,) in player_ids]
        if not player_ids:
            return []

        players = (
            db.session.query(Player)
            .filter(Player.id.in_(player_ids))
            .all()
        )

        entries: List[SeasonRatingEntry] = []
        for player in players:
            entry = SeasonRatingEngine.compute_player_entry(player, season_id, season=season)
            if entry:
                entries.append(entry)

        tiebreak_key = lambda e: (-e.season_rating, e.player_id)

        eligible = sorted(
            (e for e in entries if e.meets_top5_min_games), key=tiebreak_key
        )
        top5 = eligible[:TOP5_SLOTS]
        top5_ids = {e.player_id for e in top5}
        rest = sorted(
            (e for e in entries if e.player_id not in top5_ids), key=tiebreak_key
        )

        rank = 1
        for e in top5:
            e.rank = rank
            rank += 1

        rank = TOP5_SLOTS + 1
        for e in rest:
            e.rank = rank
            rank += 1

        return top5 + rest

    # ── Partial recalculation (single player) ─────────────────────────────────

    @staticmethod
    def recompute_player(player_id: int, season_id: int) -> Optional[SeasonRatingEntry]:
        """
        Recompute just one player's season rating — e.g. after a single
        GG adjustment or a single game correction, without rescanning
        the whole season's player pool. The caller is responsible for
        re-deriving rank if a full ordered leaderboard is needed.
        """
        player = db.session.get(Player, player_id)
        if not player:
            return None
        return SeasonRatingEngine.compute_player_entry(player, season_id)

    @staticmethod
    def get_player_rank(player_id: int, season_id: int) -> Optional[SeasonRatingEntry]:
        """Convenience: full leaderboard lookup for a single player's rank."""
        all_entries = SeasonRatingEngine.compute_season_ratings(season_id)
        return next((e for e in all_entries if e.player_id == player_id), None)

    # ── Shared "who's actually top 5" accessor ──────────────────────────────

    @staticmethod
    def top5_entries(ratings: List[SeasonRatingEntry]) -> List[SeasonRatingEntry]:
        """Entries that actually occupy ranks 1..TOP5_SLOTS (i.e. passed the
        games-played floor) — 0..TOP5_SLOTS items, already in rank order.
        Use this instead of re-deriving the games-played rule at call sites
        (season close, tiebreak, "Стол года" qualification, ...)."""
        return [e for e in ratings if e.rank <= TOP5_SLOTS]
