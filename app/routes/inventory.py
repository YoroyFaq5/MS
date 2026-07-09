from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user

from app import db
from app.models import InventoryItem, ShopCategory, Player
from app.services import ShopService
from app.auth_decorators import login_required

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/")
@login_required
def list_inventory():
    if not current_user.player_id:
        flash("Инвентарь доступен только с привязанным профилем игрока.", "warning")
        return redirect(url_for("main.index"))

    items = ShopService.get_inventory(current_user.player_id)
    grouped: dict = {}
    for inv in items:
        key = inv.item.category.value
        grouped.setdefault(key, []).append(inv)

    other_players = (
        db.session.query(Player)
        .filter(Player.is_active == True, Player.id != current_user.player_id)
        .order_by(Player.name)
        .all()
    )

    # Hero-стата — из уже загруженного списка, без новых запросов.
    total_items = len(items)
    equipped_count = sum(1 for inv in items if inv.is_equipped)
    exclusive_count = sum(1 for inv in items if inv.item.rarity.value in ("mythic", "ultra"))

    return render_template(
        "inventory/list.html", grouped=grouped, categories=list(ShopCategory),
        other_players=other_players,
        total_items=total_items, equipped_count=equipped_count,
        exclusive_count=exclusive_count,
    )


@inventory_bp.route("/<int:inventory_item_id>/equip", methods=["POST"])
@login_required
def equip(inventory_item_id: int):
    if not current_user.player_id:
        flash("Нет привязанного профиля игрока.", "danger")
        return redirect(url_for("inventory.list_inventory"))

    result = ShopService.equip_item(current_user.player, inventory_item_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("inventory.list_inventory"))


@inventory_bp.route("/<int:inventory_item_id>/unequip", methods=["POST"])
@login_required
def unequip(inventory_item_id: int):
    if not current_user.player_id:
        flash("Нет привязанного профиля игрока.", "danger")
        return redirect(url_for("inventory.list_inventory"))

    result = ShopService.unequip_item(current_user.player, inventory_item_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("inventory.list_inventory"))
