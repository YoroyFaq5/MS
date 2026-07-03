from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user

from app import db
from app.models import Player
from app.services import GiftService
from app.services.shop_service import ShopService
from app.auth_decorators import login_required

gifts_bp = Blueprint("gifts", __name__)


@gifts_bp.route("/incoming")
@login_required
def incoming():
    if not current_user.player_id:
        flash("Подарки доступны только с привязанным профилем игрока.", "warning")
        return redirect(url_for("main.index"))

    gifts = GiftService.get_incoming_gifts(current_user.player_id)
    GiftService.mark_seen(current_user.player_id)
    equipped_bulk = ShopService.get_equipped_bulk([g.from_player_id for g in gifts])
    return render_template("gifts/incoming.html", gifts=gifts, equipped_bulk=equipped_bulk)


@gifts_bp.route("/history")
@login_required
def history():
    if not current_user.player_id:
        flash("Подарки доступны только с привязанным профилем игрока.", "warning")
        return redirect(url_for("main.index"))

    transfers = GiftService.get_transfer_history(current_user.player_id)
    player_ids = {t.from_player_id for t in transfers} | {t.to_player_id for t in transfers}
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))
    return render_template(
        "gifts/history.html", transfers=transfers, my_player_id=current_user.player_id,
        equipped_bulk=equipped_bulk,
    )


@gifts_bp.route("/send", methods=["POST"])
@login_required
def send():
    if not current_user.player_id:
        flash("Нет привязанного профиля игрока.", "danger")
        return redirect(url_for("inventory.list_inventory"))

    inventory_item_id = request.form.get("inventory_item_id", type=int)
    to_player_id = request.form.get("to_player_id", type=int)
    message = request.form.get("message", "")

    if not inventory_item_id or not to_player_id:
        flash("Выберите предмет и получателя.", "danger")
        return redirect(url_for("inventory.list_inventory"))

    result = GiftService.send_gift(current_user.player, inventory_item_id, to_player_id, message)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("inventory.list_inventory"))
