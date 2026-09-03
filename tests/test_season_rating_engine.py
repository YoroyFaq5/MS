"""
Task 1 — top-5 places require >= MIN_GAMES_FOR_TOP5 (8) ranked games this
season. Centralized in SeasonRatingEngine.compute_season_ratings.
"""
from app.services.season_rating_engine import SeasonRatingEngine
from helpers import make_player, make_season, play_ranked_game, give_player_games


def test_7_games_high_score_misses_top5_8_games_makes_it(app_ctx):
    season = make_season()

    veteran = make_player("Veteran")
    give_player_games(veteran, season, count=8, won=True, points=1.0)  # 8 wins, WR=1.0, points=8

    high_scorer = make_player("HighScorer7")
    give_player_games(high_scorer, season, count=7, won=True, points=100.0)  # far higher raw score, only 7 games

    ratings = SeasonRatingEngine.compute_season_ratings(season.id)
    by_pid = {r.player_id: r for r in ratings}

    assert by_pid[high_scorer.id].games_played == 7
    assert by_pid[high_scorer.id].meets_top5_min_games is False
    assert by_pid[high_scorer.id].rank >= 6, "7-game player must never rank 1-5 regardless of score"

    assert by_pid[veteran.id].games_played == 8
    assert by_pid[veteran.id].meets_top5_min_games is True
    assert by_pid[veteran.id].rank == 1, "the only eligible (8-game) player must take rank 1"


def test_fewer_than_5_eligible_leaves_gap_before_rank_6(app_ctx):
    season = make_season()

    # Only 2 players meet the 8-game floor.
    eligible_a = make_player("EligibleA")
    give_player_games(eligible_a, season, count=8, won=True, points=10.0)
    eligible_b = make_player("EligibleB")
    give_player_games(eligible_b, season, count=8, won=True, points=9.0)

    # A 3rd player has a huge score but only 3 games — must NOT backfill rank 3.
    ineligible = make_player("Ineligible")
    give_player_games(ineligible, season, count=3, won=True, points=1000.0)

    ratings = SeasonRatingEngine.compute_season_ratings(season.id)
    by_pid = {r.player_id: r for r in ratings}

    assert by_pid[eligible_a.id].rank == 1
    assert by_pid[eligible_b.id].rank == 2
    # Ranks 3, 4, 5 are simply skipped — next player (ineligible, however
    # high-scoring) starts at rank 6, not rank 3.
    assert by_pid[ineligible.id].rank == 6


def test_rank_beyond_5_ignores_min_games_and_orders_by_score(app_ctx):
    season = make_season()

    # 5 eligible players fill ranks 1-5.
    for i in range(5):
        p = make_player(f"Top{i}")
        give_player_games(p, season, count=8, won=True, points=10.0 - i)

    # Below the top-5 cutoff, both an eligible "overflow" player and an
    # ineligible low-game player are ranked purely by score, starting at 6.
    overflow = make_player("Overflow")
    give_player_games(overflow, season, count=8, won=True, points=5.0)
    low_game_high_score = make_player("LowGameHighScore")
    give_player_games(low_game_high_score, season, count=1, won=True, points=50.0)

    ratings = SeasonRatingEngine.compute_season_ratings(season.id)
    by_pid = {r.player_id: r for r in ratings}

    assert by_pid[low_game_high_score.id].rank == 6, "higher score wins the 'rest' ordering regardless of games played"
    assert by_pid[overflow.id].rank == 7


def test_deterministic_tiebreak_by_player_id(app_ctx):
    season = make_season()
    a = make_player("Alpha")
    b = make_player("Bravo")
    give_player_games(a, season, count=8, won=True, points=1.0)
    give_player_games(b, season, count=8, won=True, points=1.0)

    ratings_1 = SeasonRatingEngine.compute_season_ratings(season.id)
    ratings_2 = SeasonRatingEngine.compute_season_ratings(season.id)

    order_1 = [r.player_id for r in ratings_1]
    order_2 = [r.player_id for r in ratings_2]
    assert order_1 == order_2
    # Lower player_id wins ties, deterministically.
    lower_id = min(a.id, b.id)
    assert order_1[0] == lower_id


def test_ineligible_player_still_visible_in_table(app_ctx):
    season = make_season()
    p = make_player("Newbie")
    give_player_games(p, season, count=2, won=True, points=1.0)

    ratings = SeasonRatingEngine.compute_season_ratings(season.id)
    assert len(ratings) == 1
    assert ratings[0].player_id == p.id
    assert ratings[0].games_needed_for_top5 == 6
