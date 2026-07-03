"""
SeasonRatingEngine
===================
Aggregate, season-scoped rating. Completely independent from ELO.

    SeasonRating = (TotalPoints * WR%) + (GG * 0.2)

Where:
    TotalPoints — sum of GameSlot.total_score (base + bonus) within the season
    WR%         — wins / games_played for that season (0..1)
    GG          — sum of active GG bonuses for that player in that season
                  (GGService.get_player_season_gg_total — strictly season-scoped)

Design rules:
    - Deterministic: same DB state → same numbers, every time.
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

# Formula weight for the GG term — fixed per spec (GG * 0.2)
GG_WEIGHT = 0.2


@dataclass
class SeasonRatingEntry:
    player_id: int
    display_name: str
    games_played: int = 0
    games_won: int = 0
    win_rate: float = 0.0          # WR%  — 0..1 (not 0..100)
    total_points: float = 0.0      # sum of GameSlot.total_score this season
    gg_total: float = 0.0          # sum of active GG entries this season
    season_rating: float = 0.0     # final composite score
    elo: float = 1000.0            # current global ELO (informational — not part of the formula)
    rank: int = 0

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
            "season_rating": round(self.season_rating, 2),
            "elo": round(self.elo, 1),
        }


class SeasonRatingEngine:

    # ── Core formula (pure function — easy to unit test) ──────────────────────

    @staticmethod
    def compute_season_rating(
        total_points: float, win_rate: float, gg_total: float
    ) -> float:
        """
        SeasonRating = (TotalPoints * WR%) + (GG * 0.2)
        win_rate must be in [0, 1].
        """
        return round((total_points * win_rate) + (gg_total * GG_WEIGHT), 4)

    # ── Per-player aggregate (no DB writes — pure read+compute) ──────────────

    @staticmethod
    def compute_player_entry(player: Player, season_id: int) -> Optional[SeasonRatingEntry]:
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
            total_points, win_rate, gg_total
        )

        return SeasonRatingEntry(
            player_id=player.id,
            display_name=player.display_name,
            games_played=games_played,
            games_won=games_won,
            win_rate=win_rate,
            total_points=round(total_points, 2),
            gg_total=gg_total,
            season_rating=rating,
            elo=player.elo,
        )

    # ── Full season recalculation ──────────────────────────────────────────────

    @staticmethod
    def compute_season_ratings(season_id: int) -> List[SeasonRatingEntry]:
        """
        Full recalculation for every player who played a ranked game
        in this season. Stateless — does not write anything to the DB;
        callers decide whether/how to persist or cache the result.
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
            entry = SeasonRatingEngine.compute_player_entry(player, season_id)
            if entry:
                entries.append(entry)

        entries.sort(key=lambda e: -e.season_rating)
        for i, e in enumerate(entries, start=1):
            e.rank = i

        return entries

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
