"""
Bot API (/api/v1/bot/*) — security-critical behaviour:
  - hide_standings leak is closed (task: "Скрытый рейтинг турнира нельзя
    получить через Bot API").
  - auth requires the exact service token (constant-time compare doesn't
    change correctness, just timing-safety, but wrong/missing tokens must
    still be rejected).
  - a mutating endpoint can't be used to act on another player's resources
    just by knowing their telegram_id vs. an arbitrary draft/inventory id
    they don't own (ownership is re-checked server-side regardless of what
    the bot forwards).
"""
import pytest

from app import db
from app.models import User
from helpers import make_player, make_tournament

TOKEN = "test-service-token"


@pytest.fixture(autouse=True)
def _service_token(app):
    app.config["MAIN_API_SERVICE_TOKEN"] = TOKEN
    yield


def _auth(extra=None):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    if extra:
        headers.update(extra)
    return headers


def _link_player(player, telegram_id="555000111"):
    player.telegram_id = telegram_id
    db.session.commit()


def test_bot_api_requires_correct_token(app_ctx, client):
    t = make_tournament("Bot API Cup", status="active")
    resp = client.get(f"/api/v1/bot/tournaments/{t.id}", headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401

    resp = client.get(f"/api/v1/bot/tournaments/{t.id}")
    assert resp.status_code == 401


def test_hidden_standings_not_leaked_to_anonymous_bot_caller(app_ctx, client):
    t = make_tournament("Hidden Cup", status="active")
    t.hide_standings = True
    db.session.commit()

    resp = client.get(f"/api/v1/bot/tournaments/{t.id}", headers=_auth())
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["can_view_standings"] is False
    assert data["player_ratings"] == []
    assert data["team_ratings"] == []


def test_hidden_standings_visible_to_non_participant_admin(app_ctx, client):
    t = make_tournament("Hidden Cup 2", status="active")
    t.hide_standings = True
    db.session.commit()

    admin_player = make_player("AdminViewer")
    _link_player(admin_player, "555000222")
    user = User(username="admin_viewer", is_admin=True, player_id=admin_player.id)
    user.set_password("x")
    db.session.add(user)
    db.session.commit()

    resp = client.get(
        f"/api/v1/bot/tournaments/{t.id}",
        query_string={"telegram_id": "555000222"},
        headers=_auth(),
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["can_view_standings"] is True


def test_hidden_standings_still_hidden_from_participant_admin(app_ctx, client):
    """An admin who is themselves playing in the tournament must not be
    able to peek at the hidden standings through the bot either — same
    rule as the website (tournaments.py::_can_view_standings)."""
    from app.services.tournament_service import TournamentService

    t = make_tournament("Hidden Cup 3", status="pending")
    admin_player = make_player("PlayingAdmin")
    _link_player(admin_player, "555000333")
    user = User(username="playing_admin", is_admin=True, player_id=admin_player.id)
    user.set_password("x")
    db.session.add(user)
    db.session.commit()

    TournamentService.register_participant(t.id, admin_player.id)
    t.hide_standings = True
    db.session.commit()

    resp = client.get(
        f"/api/v1/bot/tournaments/{t.id}",
        query_string={"telegram_id": "555000333"},
        headers=_auth(),
    )
    data = resp.get_json()["data"]
    assert data["can_view_standings"] is False


def test_shop_buy_requires_linked_player(app_ctx, client):
    resp = client.post(
        "/api/v1/bot/shop/items/1/buy", json={"telegram_id": "000nonexistent"}, headers=_auth(),
    )
    assert resp.status_code == 404


def test_gifts_cannot_send_someone_elses_inventory_item(app_ctx, client):
    """Owning telegram_id A can't gift inventory_item_id belonging to
    player B just by naming its id — GiftService checks ownership."""
    from app.models import ShopItem, InventoryItem, ShopCategory, Rarity

    owner = make_player("ItemOwner")
    attacker = make_player("Attacker")
    _link_player(attacker, "555000444")

    item = ShopItem(
        name="Frame", category=ShopCategory.PROFILE_CUSTOMIZATION, subcategory="frame",
        rarity=Rarity.COMMON, price=10.0,
    )
    db.session.add(item)
    db.session.flush()
    inv = InventoryItem(player_id=owner.id, item_id=item.id, price_paid=10.0)
    db.session.add(inv)
    db.session.commit()

    resp = client.post("/api/v1/bot/gifts/send", json={
        "telegram_id": "555000444", "inventory_item_id": inv.id, "to_player_id": owner.id,
    }, headers=_auth())
    assert resp.status_code >= 400
    db.session.refresh(inv)
    assert inv.player_id == owner.id, "ownership must not have changed"
