"""
Task 2 — GG weight is versioned per-season (Season.gg_weight), not a single
global constant: existing/historical seasons keep 0.2 forever, seasons
created going forward get 0.1.
"""
from app import db
from app.models import GG
from app.services.season_rating_engine import SeasonRatingEngine
from app.services.season_service import SeasonService, NEW_SEASON_GG_WEIGHT
from helpers import make_player, make_season, give_player_games


def _add_gg(player, season, value):
    gg = GG(player_id=player.id, season_id=season.id, value=value, reason="test bonus")
    db.session.add(gg)
    db.session.flush()
    return gg


def test_old_season_uses_0_2_new_season_uses_0_1(app_ctx):
    old_season = make_season(year=2023, number=1, gg_weight=0.2)
    new_season = make_season(year=2024, number=1, gg_weight=0.1)

    player = make_player("GGPlayer")
    give_player_games(player, old_season, count=1, won=True, points=10.0)
    _add_gg(player, old_season, 5.0)

    player2 = make_player("GGPlayer2")
    give_player_games(player2, new_season, count=1, won=True, points=10.0)
    _add_gg(player2, new_season, 5.0)

    old_entry = SeasonRatingEngine.compute_player_entry(player, old_season.id)
    new_entry = SeasonRatingEngine.compute_player_entry(player2, new_season.id)

    # base = TotalPoints * WR% = 10 * 1.0 = 10 for both.
    assert old_entry.season_rating == 10.0 + 5.0 * 0.2
    assert new_entry.season_rating == 10.0 + 5.0 * 0.1
    assert old_entry.gg_weight == 0.2
    assert new_entry.gg_weight == 0.1


def test_ensure_year_exists_creates_new_seasons_with_0_1(app_ctx):
    seasons = SeasonService.ensure_year_exists(2099)
    assert len(seasons) == 6
    for s in seasons:
        assert s.gg_weight == NEW_SEASON_GG_WEIGHT
        assert s.gg_weight == 0.1


def test_historical_result_unchanged_after_recompute(app_ctx):
    """Recomputing an old season's rating must reproduce exactly the same
    number every time — the weight is fixed on the Season row, not derived
    from "is this the newest season" at compute time."""
    old_season = make_season(year=2020, number=1, gg_weight=0.2)
    player = make_player("Historic")
    give_player_games(player, old_season, count=1, won=True, points=8.0)
    _add_gg(player, old_season, 10.0)

    first = SeasonRatingEngine.compute_player_entry(player, old_season.id).season_rating

    # Simulate time passing / new seasons being created elsewhere — must
    # not affect this season's own fixed gg_weight or its result.
    SeasonService.ensure_year_exists(2030)

    second = SeasonRatingEngine.compute_player_entry(player, old_season.id).season_rating
    assert first == second == (8.0 * 1.0) + (10.0 * 0.2)
