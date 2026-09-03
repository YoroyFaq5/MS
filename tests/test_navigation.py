"""
Task 4 — centralized, safe context redirects:
  - NavigationService resolves back/redirect targets purely from server-
    validated tournament_id/stage_id (no open-redirect surface).
  - A tournament game returns to its tournament; a series evening's game
    returns to that evening, not the tournament wrapper or the games list;
    a standalone game returns to the general games list.
"""
from app import db
from app.models import Role, WinSide, GameSlot
from app.services.navigation_service import NavigationService
from helpers import (
    make_player, make_tournament, make_series_tournament, add_series_evening,
    make_admin_user,
)
from conftest import login_as


def test_game_context_url_standalone_falls_back_to_games_list(app_ctx):
    url = NavigationService.game_context_url(None, None)
    assert url.endswith("/games/")


def test_game_context_url_plain_tournament(app_ctx):
    t = make_tournament("Plain Cup")
    url = NavigationService.game_context_url(t.id, None)
    assert f"/tournaments/{t.id}" in url
    assert "/series-tournaments/" not in url


def test_game_context_url_series_evening_goes_to_evening_not_wrapper(app_ctx):
    t, st = make_series_tournament("Series Cup")
    evening = add_series_evening(st, "Вечер 1")

    url = NavigationService.game_context_url(t.id, evening.stage_id)
    assert f"/series-tournaments/{st.id}/series/{evening.id}" in url
    # Must NOT be the series-tournament wrapper page itself.
    assert url.rstrip("/") != f"/series-tournaments/{st.id}"


def test_tournament_view_url_series_aware(app_ctx):
    plain = make_tournament("Plain2")
    url = NavigationService.tournament_view_url(plain.id)
    assert f"/tournaments/{plain.id}" in url
    assert "/series-tournaments/" not in url

    t, st = make_series_tournament("Series2")
    url = NavigationService.tournament_view_url(t.id)
    assert f"/series-tournaments/{st.id}" in url
    assert f"/tournaments/{t.id}" not in url


def _finish_form(win_side="city"):
    return {"win_side": win_side}


def test_finish_game_in_plain_tournament_redirects_to_tournament(app_ctx, client):
    admin = make_admin_user()
    t = make_tournament("FinishCup", status="active")
    from helpers import play_ranked_game, make_season
    season = make_season(year=2040, number=1)
    p1 = make_player("F1")
    p2 = make_player("F2")
    game = play_ranked_game(p1, season, won=True, points=1.0, tournament_id=t.id)
    game.is_finished = False
    slot2 = GameSlot(game_id=game.id, player_id=p2.id, seat_number=2, role=Role.MAFIA)
    db.session.add(slot2)
    db.session.commit()

    login_as(client, admin)
    resp = client.post(f"/games/{game.id}/finish", data=_finish_form(), follow_redirects=False)
    assert resp.status_code == 302
    assert f"/tournaments/{t.id}" in resp.headers["Location"]


def test_finish_game_in_series_evening_redirects_to_evening(app_ctx, client):
    admin = make_admin_user()
    t, st = make_series_tournament("FinishSeries")
    evening = add_series_evening(st, "Вечер А")

    from helpers import play_ranked_game, make_season
    season = make_season(year=2041, number=1)
    p1 = make_player("SF1")
    p2 = make_player("SF2")
    game = play_ranked_game(p1, season, won=True, points=1.0, tournament_id=t.id, stage_id=evening.stage_id)
    game.is_finished = False
    slot2 = GameSlot(game_id=game.id, player_id=p2.id, seat_number=2, role=Role.MAFIA)
    db.session.add(slot2)
    db.session.commit()

    login_as(client, admin)
    resp = client.post(f"/games/{game.id}/finish", data=_finish_form(), follow_redirects=False)
    assert resp.status_code == 302
    assert f"/series-tournaments/{st.id}/series/{evening.id}" in resp.headers["Location"]


def test_finish_standalone_game_redirects_to_its_own_page(app_ctx, client):
    admin = make_admin_user()
    from helpers import play_ranked_game, make_season
    season = make_season(year=2042, number=1)
    p1 = make_player("ST1")
    p2 = make_player("ST2")
    game = play_ranked_game(p1, season, won=True, points=1.0)
    game.is_finished = False
    slot2 = GameSlot(game_id=game.id, player_id=p2.id, seat_number=2, role=Role.MAFIA)
    db.session.add(slot2)
    db.session.commit()

    login_as(client, admin)
    resp = client.post(f"/games/{game.id}/finish", data=_finish_form(), follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].rstrip("/").endswith(f"/games/{game.id}")


def test_new_game_page_cancel_link_targets_tournament_context(app_ctx, client):
    admin = make_admin_user()
    t = make_tournament("ContextCup", status="pending")
    login_as(client, admin)

    resp = client.get(f"/games/new?tournament_id={t.id}")
    assert resp.status_code == 200
    assert f'href="http://testserver.local/tournaments/{t.id}"'.encode() in resp.data or \
        f"/tournaments/{t.id}".encode() in resp.data


def test_new_game_rejects_open_redirect_style_next_param(app_ctx, client):
    """There is no client-controllable redirect target at all — the page
    only ever derives it from server-validated tournament_id/stage_id, so
    an attacker-supplied `next`/`return_to` value can't do anything."""
    admin = make_admin_user()
    login_as(client, admin)

    resp = client.get("/games/new?next=https://evil.example.com&tournament_id=999999")
    assert resp.status_code == 200
    assert b"evil.example.com" not in resp.data
