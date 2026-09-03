"""
Task 4 — series-tournament cards on /tournaments/ must route into the
series interface (Открыть/Рейтинг), not the plain tournament UI, and must
not offer the plain "Этапы" bracket action (meaningless/unsafe for a
series — see tournaments.py::_SERIES_ACTION_BLOCKED_MSG for why the
underlying actions are blocked; the card should not even point there).
"""
from helpers import make_series_tournament, make_tournament, add_series_evening


def test_series_card_links_to_series_interface(app_ctx, client):
    t, st = make_series_tournament("Card Series")
    # An ACTIVE plain tournament always wins the single "featured" slot
    # (see tournaments.py::list_tournaments), which pushes the series
    # tournament into the grid below — that's where the per-card action
    # links (Открыть/Рейтинг/Этапы) being asserted on actually live.
    make_tournament("Other Plain Tournament", status="active")

    resp = client.get("/tournaments/")
    assert resp.status_code == 200
    body = resp.data.decode()

    assert f"/series-tournaments/{st.id}" in body
    # The plain tournament-detail/leaderboard/stages URLs for THIS
    # tournament id must not appear as an action target.
    assert f'href="/tournaments/{t.id}"' not in body
    assert f"tournaments/{t.id}/leaderboard" not in body
    assert f"tournaments/{t.id}/stages" not in body
