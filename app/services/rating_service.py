"""
Rating Service  (extended — v2)
================================
Handles global rating AND tournament/stage/team scoped ratings.

Design rules:
- Pure Python + SQLAlchemy ORM.  No Flask imports.
- All new methods are additive — original compute_all_ratings() unchanged.
- is_ranked flag on Game controls global rating inclusion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from sqlalchemy.orm import contains_eager

from app import db
from app.models import Player, GameSlot, Game, Role, WinSide


# ---------------------------------------------------------------------------
# Base score table  (unchanged)
# ---------------------------------------------------------------------------

# ── New scoring: 1 point for win, 0 for loss — all roles equal ──────────────
# bonus_score (float, admin-assigned) is added on top via GameSlot.bonus_score.
BASE_SCORES: dict[tuple[Role, WinSide], float] = {
    # Mafia side wins
    (Role.MAFIA,    WinSide.MAFIA): 1.0,
    (Role.DON,      WinSide.MAFIA): 1.0,
    # Mafia side loses
    (Role.MAFIA,    WinSide.CITY):  0.0,
    (Role.DON,      WinSide.CITY):  0.0,
    # City side wins
    (Role.CIVILIAN, WinSide.CITY):  1.0,
    (Role.SHERIFF,  WinSide.CITY):  1.0,
    # City side loses
    (Role.CIVILIAN, WinSide.MAFIA): 0.0,
    (Role.SHERIFF,  WinSide.MAFIA): 0.0,
    # Draw / unfinished
    (Role.MAFIA,    WinSide.NONE):  0.0,
    (Role.DON,      WinSide.NONE):  0.0,
    (Role.CIVILIAN, WinSide.NONE):  0.0,
    (Role.SHERIFF,  WinSide.NONE):  0.0,
}


def calculate_base_score(role: Role, win_side: WinSide) -> float:
    return BASE_SCORES.get((role, win_side), 0.0)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------

@dataclass
class PlayerRating:
    player_id: int
    player_name: str
    display_name: str
    games_played: int = 0
    games_won: int = 0
    total_score: float = 0.0
    avg_score: float = 0.0
    mafia_games: int = 0
    city_games: int = 0
    sheriff_games: int = 0
    don_games: int = 0
    win_rate: float = 0.0
    rank: int = 0
    elo: float = 1000.0

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "display_name": self.display_name,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": round(self.win_rate, 1),
            "total_score": round(self.total_score, 2),
            "avg_score": round(self.avg_score, 2),
            "mafia_games": self.mafia_games,
            "city_games": self.city_games,
            "sheriff_games": self.sheriff_games,
            "don_games": self.don_games,
            "elo": round(self.elo, 1),
        }


@dataclass
class TeamRating:
    team_id: int
    team_name: str
    color: Optional[str]
    member_count: int = 0
    games_played: int = 0
    games_won: int = 0
    total_score: float = 0.0
    avg_score: float = 0.0
    win_rate: float = 0.0
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "color": self.color,
            "member_count": self.member_count,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": round(self.win_rate, 1),
            "total_score": round(self.total_score, 2),
            "avg_score": round(self.avg_score, 2),
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _slots_to_player_rating(player: Player, slots: Sequence[GameSlot]) -> PlayerRating:
    """Aggregate a list of GameSlots into a PlayerRating DTO."""
    pr = PlayerRating(
        player_id=player.id,
        player_name=player.name,
        display_name=player.display_name,
        elo=player.elo,
    )
    for slot in slots:
        pr.games_played += 1
        pr.total_score += slot.total_score
        if slot.role == Role.MAFIA:
            pr.mafia_games += 1
        elif slot.role == Role.DON:
            pr.don_games += 1
        elif slot.role == Role.SHERIFF:
            pr.sheriff_games += 1
        else:
            pr.city_games += 1

        game = slot.game
        won = (
            (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
            or (slot.is_city_side and game.win_side == WinSide.CITY)
        )
        if won:
            pr.games_won += 1

    if pr.games_played > 0:
        pr.avg_score = round(pr.total_score / pr.games_played, 2)
        pr.win_rate = round(pr.games_won / pr.games_played * 100, 1)

    return pr


def _rank(ratings: list) -> list:
    ratings.sort(key=lambda r: (-r.total_score, -r.avg_score))
    for idx, r in enumerate(ratings, 1):
        r.rank = idx
    return ratings


# ---------------------------------------------------------------------------
# RatingService
# ---------------------------------------------------------------------------

class RatingService:

    # ── Global rating ────────────────────────────────────────────────────────

    @staticmethod
    def compute_all_ratings() -> List[PlayerRating]:
        """
        Global rating: only finished, is_ranked=True games count.
        Original API preserved.

        Fetches all qualifying slots in a single query and groups them in
        Python, instead of one query per player (was O(active_players)
        round-trips per call — noticeable when this runs once per game,
        as it does via the top1_global achievement check).
        """
        players = (
            db.session.query(Player)
            .filter(Player.is_active == True)
            .all()
        )
        all_slots = (
            db.session.query(GameSlot)
            .join(Game)
            .options(contains_eager(GameSlot.game))
            .filter(Game.is_finished == True, Game.is_ranked == True)
            .all()
        )
        slots_by_player: dict[int, list] = {}
        for slot in all_slots:
            slots_by_player.setdefault(slot.player_id, []).append(slot)

        ratings: List[PlayerRating] = []
        for player in players:
            slots = slots_by_player.get(player.id)
            if not slots:
                continue
            ratings.append(_slots_to_player_rating(player, slots))
        return _rank(ratings)

    @staticmethod
    def get_global_rating() -> List[PlayerRating]:
        """Alias for compute_all_ratings() — explicit name for API clarity."""
        return RatingService.compute_all_ratings()

    @staticmethod
    def get_player_rating(player_id: int) -> Optional[PlayerRating]:
        all_ratings = RatingService.compute_all_ratings()
        return next((r for r in all_ratings if r.player_id == player_id), None)

    # ── Tournament scoped ────────────────────────────────────────────────────

    @staticmethod
    def get_tournament_rating(tournament_id: int) -> List[PlayerRating]:
        """
        Rating across ALL stages/games of a tournament.
        Only finished games inside this tournament are aggregated.
        """
        players_in_tourney = (
            db.session.query(Player)
            .join(Player.tournament_participations)
            .filter_by(tournament_id=tournament_id)
            .all()
        )
        ratings: List[PlayerRating] = []
        for player in players_in_tourney:
            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == player.id,
                    Game.is_finished == True,
                    Game.tournament_id == tournament_id,
                )
                .all()
            )
            if not slots:
                pr = PlayerRating(
                    player_id=player.id,
                    player_name=player.name,
                    display_name=player.display_name,
                    elo=player.elo,
                )
                ratings.append(pr)
                continue
            ratings.append(_slots_to_player_rating(player, slots))
        return _rank(ratings)

    # ── Stage scoped ─────────────────────────────────────────────────────────

    @staticmethod
    def get_stage_rating(stage_id: int) -> List[PlayerRating]:
        """Rating scoped to a single tournament stage."""
        from app.models import TournamentParticipant, TournamentStage
        stage = db.session.get(TournamentStage, stage_id)
        if not stage:
            return []

        players_in_tourney = (
            db.session.query(Player)
            .join(Player.tournament_participations)
            .filter_by(tournament_id=stage.tournament_id)
            .all()
        )
        ratings: List[PlayerRating] = []
        for player in players_in_tourney:
            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == player.id,
                    Game.is_finished == True,
                    Game.stage_id == stage_id,
                )
                .all()
            )
            if not slots:
                continue
            ratings.append(_slots_to_player_rating(player, slots))
        return _rank(ratings)

    # ── Team rating ──────────────────────────────────────────────────────────

    @staticmethod
    def get_team_rating(tournament_id: int) -> List[TeamRating]:
        """
        Team rating = sum of all member scores within tournament games.
        Each game slot contributes to its player's team.
        """
        from app.models import Team, TeamPlayer

        teams = (
            db.session.query(Team)
            .filter_by(tournament_id=tournament_id)
            .all()
        )
        ratings: List[TeamRating] = []

        for team in teams:
            tr = TeamRating(
                team_id=team.id,
                team_name=team.name,
                color=team.color,
                member_count=len(team.members),
            )
            # Aggregate individual scores of all team members in this tournament
            member_player_ids = [m.player_id for m in team.members]
            if not member_player_ids:
                ratings.append(tr)
                continue

            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id.in_(member_player_ids),
                    Game.is_finished == True,
                    Game.tournament_id == tournament_id,
                )
                .all()
            )
            for slot in slots:
                tr.games_played += 1
                tr.total_score += slot.total_score
                game = slot.game
                won = (
                    (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
                    or (slot.is_city_side and game.win_side == WinSide.CITY)
                )
                if won:
                    tr.games_won += 1

            if tr.games_played > 0:
                tr.avg_score = round(tr.total_score / tr.games_played, 2)
                tr.win_rate = round(tr.games_won / tr.games_played * 100, 1)

            ratings.append(tr)

        return _rank(ratings)

    # ── Apply scores ─────────────────────────────────────────────────────────

    # ── Season scoped ratings ────────────────────────────────────────────────

    @staticmethod
    def get_season_rating(season_id: int) -> List["SeasonRatingEntry"]:
        """
        Season rating using the canonical SeasonRatingEngine formula:
            SeasonRating = (TotalPoints * WR%) + (GG * 0.2)

        Returns SeasonRatingEntry list (not PlayerRating) — callers that
        only need rank/display_name/total use .season_rating attribute.
        """
        from app.services.season_rating_engine import SeasonRatingEngine
        return SeasonRatingEngine.compute_season_ratings(season_id)

    @staticmethod
    def get_year_rating(year: int) -> List[PlayerRating]:
        """
        Aggregate rating across all 6 seasons of a calendar year.
        Only ranked games whose played_at falls within that year.
        """
        from app.models import Season
        from sqlalchemy import extract

        players = db.session.query(Player).filter_by(is_active=True).all()
        ratings: List[PlayerRating] = []

        # Collect all season IDs for the year
        season_ids = [
            s.id for s in
            db.session.query(Season).filter_by(year=year).all()
        ]
        if not season_ids:
            return []

        for player in players:
            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == player.id,
                    Game.is_finished == True,
                    Game.is_ranked == True,
                    Game.season_id.in_(season_ids),
                )
                .all()
            )
            if not slots:
                continue
            ratings.append(_slots_to_player_rating(player, slots))

        return _rank(ratings)

    @staticmethod
    def get_player_season_rating(player_id: int, season_id: int) -> Optional[PlayerRating]:
        ratings = RatingService.get_season_rating(season_id)
        return next((r for r in ratings if r.player_id == player_id), None)

    @staticmethod
    def apply_base_scores_to_game(game: Game, commit: bool = False) -> None:
        """
        Recalculate and persist base_score for all slots in a finished game.
        commit defaults to False since this is normally the first step of
        PostGameOrchestrator.run(), which commits once at the end of the
        pipeline; pass commit=True when calling this standalone.
        """
        for slot in game.slots:
            slot.base_score = calculate_base_score(slot.role, game.win_side)
        if commit:
            db.session.commit()


