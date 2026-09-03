"""Shared test data builders — kept dead simple: each "game" exists only to
give one player one ranked/finished GameSlot in a season, which is all
SeasonRatingEngine/RatingService.get_season_rating need. Real games have 10
seats; nothing here relies on that, so tests build the minimum each
scenario needs instead of a full 10-player table.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app import db
from app.models import (
    Player, Season, SeasonStatus, Game, GameSlot, Role, WinSide,
    Tournament, TournamentType, TournamentStage, StageType,
    TournamentParticipant, SeriesTournament, TournamentSeries, SeriesStatus,
)
from app.models.user import User


def make_player(name: str, is_active: bool = True, elo: float = 1000.0) -> Player:
    p = Player(name=name, nickname=name, is_active=is_active, elo=elo)
    db.session.add(p)
    db.session.flush()
    return p


def make_admin_user(username: str = "admin") -> User:
    u = User(username=username, is_admin=True, is_active=True)
    u.set_password("hunter2")
    db.session.add(u)
    db.session.flush()
    return u


def make_season(
    year: int = 2024, number: int = 1, status: SeasonStatus = SeasonStatus.FINISHED,
    gg_weight: float = 0.2,
) -> Season:
    s = Season(
        year=year, number=number, name=f"Сезон {number} тест {year}",
        starts_at=datetime(year, 1, 1, tzinfo=timezone.utc),
        ends_at=datetime(year, 12, 31, tzinfo=timezone.utc),
        status=status, gg_weight=gg_weight,
    )
    db.session.add(s)
    db.session.flush()
    return s


def play_ranked_game(
    player: Player, season: Season, won: bool, points: float = 1.0,
    tournament_id=None, stage_id=None, is_finished: bool = True, is_ranked: bool = True,
) -> Game:
    """One finished ranked game giving `player` a single GameSlot worth
    `points` base_score, won or lost as requested."""
    game = Game(
        win_side=WinSide.CITY if won else WinSide.MAFIA,
        is_finished=is_finished,
        is_ranked=is_ranked,
        season_id=season.id,
        tournament_id=tournament_id,
        stage_id=stage_id,
    )
    db.session.add(game)
    db.session.flush()
    slot = GameSlot(
        game_id=game.id, player_id=player.id, seat_number=1,
        role=Role.CIVILIAN, base_score=points, bonus_score=0.0,
    )
    db.session.add(slot)
    db.session.flush()
    return game


def give_player_games(player: Player, season: Season, count: int, won: bool = True, points: float = 1.0):
    for _ in range(count):
        play_ranked_game(player, season, won=won, points=points)


def make_tournament(name: str, status: str = "pending", t_type: TournamentType = TournamentType.INDIVIDUAL) -> Tournament:
    t = Tournament(name=name, type=t_type, is_ranked=True, has_stages=False, status=status)
    db.session.add(t)
    db.session.flush()
    return t


def make_series_tournament(name: str, status: str = "pending") -> tuple[Tournament, SeriesTournament]:
    t = make_tournament(name, status=status)
    t.has_stages = True
    st = SeriesTournament(tournament_id=t.id)
    db.session.add(st)
    db.session.flush()
    return t, st


def add_series_evening(series_tournament: SeriesTournament, name: str, order: int = 1) -> TournamentSeries:
    stage = TournamentStage(
        tournament_id=series_tournament.tournament_id, name=name, order=order,
        type=StageType.GROUP, status="active",
    )
    db.session.add(stage)
    db.session.flush()
    series = TournamentSeries(
        series_tournament_id=series_tournament.id, stage_id=stage.id,
        name=name, order=order, status=SeriesStatus.ACTIVE,
    )
    db.session.add(series)
    db.session.flush()
    return series
