"""
Task 3 — "Стол года" qualification and sync:
  - 2+2+2+2+2+1 slots across seasons 1-5 / 6, earlier season priority,
    year-wide uniqueness, min-games/top-5 restriction (task 1).
  - Re-sync is idempotent and only adds/removes STALE AUTO rows while the
    year tournament is "pending"; manual registrations are never touched.
  - An active/finished year tournament never gets its composition changed
    silently.
"""
from app import db
from app.models import SeasonStatus, TournamentParticipant
from app.services.season_service import SeasonService
from helpers import make_player, make_season, give_player_games


def _qualify(player, season, rank_points=10.0):
    """Give a player exactly the games needed to occupy a top-5 season
    place with a distinct score (rank_points controls ordering)."""
    give_player_games(player, season, count=8, won=True, points=rank_points)


def test_qualifier_slot_distribution_2_2_2_2_2_1(app_ctx):
    year = 2050
    players = {}
    for number in range(1, 7):
        season = make_season(year=year, number=number, status=SeasonStatus.FINISHED)
        # 3 candidates per season so we can see exactly `slots` get picked.
        for rank in range(3):
            p = make_player(f"S{number}P{rank}")
            _qualify(p, season, rank_points=10.0 - rank)
            players[(number, rank)] = p

    qualifiers = SeasonService.compute_year_qualifiers(year)
    assert len(qualifiers) == 6

    for season, picks in qualifiers:
        expected_slots = 1 if season.number == 6 else 2
        assert len(picks) == expected_slots, f"season {season.number} expected {expected_slots} picks"


def test_min_games_and_top5_restriction_applies_to_qualification(app_ctx):
    year = 2051
    season = make_season(year=year, number=1, status=SeasonStatus.FINISHED)

    high_score_low_games = make_player("Sneaky")
    give_player_games(high_score_low_games, season, count=3, won=True, points=1000.0)

    eligible = make_player("Eligible")
    _qualify(eligible, season, rank_points=1.0)

    qualifiers = SeasonService.compute_year_qualifiers(year)
    picks = next(picks for s, picks in qualifiers if s.number == 1)
    picked_ids = {e.player_id for e in picks}

    assert eligible.id in picked_ids
    assert high_score_low_games.id not in picked_ids


def test_uniqueness_across_year_earlier_season_has_priority(app_ctx):
    year = 2052
    season1 = make_season(year=year, number=1, status=SeasonStatus.FINISHED)
    season2 = make_season(year=year, number=2, status=SeasonStatus.FINISHED)

    star = make_player("Star")
    _qualify(star, season1, rank_points=10.0)
    _qualify(star, season2, rank_points=10.0)  # same player also tops season 2

    runner_up_s2 = make_player("RunnerUpS2")
    _qualify(runner_up_s2, season2, rank_points=9.0)
    third_s2 = make_player("ThirdS2")
    _qualify(third_s2, season2, rank_points=8.0)

    qualifiers = SeasonService.compute_year_qualifiers(year)
    picks_by_season = {s.number: [e.player_id for e in picks] for s, picks in qualifiers}

    assert star.id in picks_by_season[1]
    # Star already qualified via season 1 — season 2 must skip them and
    # take the next unique players instead.
    assert star.id not in picks_by_season[2]
    assert set(picks_by_season[2]) == {runner_up_s2.id, third_s2.id}


def test_resync_is_idempotent_no_duplicates(app_ctx):
    year = 2053
    season = make_season(year=year, number=1, status=SeasonStatus.FINISHED)
    p = make_player("Idempotent")
    _qualify(p, season, rank_points=5.0)

    SeasonService._sync_year_tournament_participants(year)
    result = SeasonService._sync_year_tournament_participants(year)

    rows = db.session.query(TournamentParticipant).filter_by(
        tournament_id=result.tournament.id, player_id=p.id
    ).all()
    assert len(rows) == 1
    assert result.added == []  # second sync found nothing new to add


def test_resync_removes_only_stale_auto_rows_in_pending_tournament(app_ctx):
    year = 2054
    season1 = make_season(year=year, number=1, status=SeasonStatus.FINISHED)

    # Season 1 has exactly 2 slots — A and B both qualify initially.
    player_a = make_player("KeepsSlot")
    _qualify(player_a, season1, rank_points=10.0)
    player_b = make_player("GetsDisplaced")
    _qualify(player_b, season1, rank_points=5.0)

    sync1 = SeasonService._sync_year_tournament_participants(year)
    t = sync1.tournament
    assert t.status == "pending"
    assert {player_a.id, player_b.id} == set(
        pp.player_id for pp in
        db.session.query(TournamentParticipant).filter_by(tournament_id=t.id).all()
    )

    manual = make_player("ManualAdd")
    db.session.add(TournamentParticipant(
        tournament_id=t.id, player_id=manual.id, qualified_via_season_id=None,
    ))
    db.session.commit()

    # A new player scores higher than B (but not A) — B is pushed out of
    # season 1's top-2 slots and replaced.
    player_c = make_player("Displacer")
    _qualify(player_c, season1, rank_points=7.0)

    sync2 = SeasonService._sync_year_tournament_participants(year)

    remaining_pids = {
        p.player_id for p in
        db.session.query(TournamentParticipant).filter_by(tournament_id=t.id).all()
    }
    assert player_a.id in remaining_pids, "still-qualifying auto row is untouched"
    assert player_c.id in remaining_pids, "newly-qualifying player is added"
    assert player_b.id not in remaining_pids, "displaced auto qualifier is removed"
    assert manual.id in remaining_pids, "manual registration must survive re-sync"
    assert sync2.warning is None
    assert player_c.display_name in sync2.added
    assert player_b.display_name in sync2.removed


def test_active_year_tournament_composition_not_silently_changed(app_ctx):
    year = 2055
    season = make_season(year=year, number=1, status=SeasonStatus.FINISHED)
    p1 = make_player("P1")
    _qualify(p1, season, rank_points=10.0)

    sync1 = SeasonService._sync_year_tournament_participants(year)
    t = sync1.tournament
    t.status = "active"
    db.session.commit()

    # A new qualifier appears after the tournament went active.
    p2 = make_player("P2")
    _qualify(p2, season, rank_points=9.0)

    sync2 = SeasonService._sync_year_tournament_participants(year)

    assert sync2.warning is not None, "must warn instead of silently mutating an active tournament"
    pids = {
        pp.player_id for pp in
        db.session.query(TournamentParticipant).filter_by(tournament_id=t.id).all()
    }
    assert p2.id not in pids, "composition of an active year tournament must not change"

    result = SeasonService.create_year_tournament(year)
    assert result.ok is False
    assert "active" in result.message or "pending" in result.message or t.status in result.message


def test_finished_year_tournament_composition_not_silently_changed(app_ctx):
    year = 2056
    season = make_season(year=year, number=1, status=SeasonStatus.FINISHED)
    p1 = make_player("F1")
    _qualify(p1, season, rank_points=10.0)

    sync1 = SeasonService._sync_year_tournament_participants(year)
    t = sync1.tournament
    t.status = "finished"
    db.session.commit()

    p2 = make_player("F2")
    _qualify(p2, season, rank_points=9.0)

    sync2 = SeasonService._sync_year_tournament_participants(year)
    assert sync2.warning is not None
    pids = {
        pp.player_id for pp in
        db.session.query(TournamentParticipant).filter_by(tournament_id=t.id).all()
    }
    assert pids == {p1.id}
