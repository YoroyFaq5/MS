from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user

from app import db
from app.models import ShopItem, ShopCategory
from app.services import ShopService, PermissionService, Permission
from app.auth_decorators import requires_permission

shop_bp = Blueprint("shop", __name__)


@shop_bp.route("/")
def list_items():
    category_param = request.args.get("category")
    category = None
    if category_param:
        try:
            category = ShopCategory(category_param)
        except ValueError:
            pass

    items = ShopService.list_items(category=category)

    player = current_user.player if current_user.is_authenticated else None
    affordability = {}
    if player:
        for item in items:
            affordability[item.id] = ShopService.validate_purchase(player, item).ok

    return render_template(
        "shop/list.html",
        items=items,
        categories=list(ShopCategory),
        selected_category=category,
        affordability=affordability,
        player=player,
    )


@shop_bp.route("/<int:item_id>")
def item_detail(item_id: int):
    item = db.session.get(ShopItem, item_id) or abort(404)
    player = current_user.player if current_user.is_authenticated else None
    validation = ShopService.validate_purchase(player, item) if player else None
    return render_template("shop/detail.html", item=item, player=player, validation=validation)


@shop_bp.route("/<int:item_id>/purchase", methods=["POST"])
@requires_permission(Permission.PURCHASE_ITEM)
def purchase_item(item_id: int):
    if not current_user.player_id:
        flash("Для покупок нужен привязанный профиль игрока.", "warning")
        return redirect(url_for("shop.item_detail", item_id=item_id))

    result = ShopService.purchase(current_user.player, item_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("shop.item_detail", item_id=item_id))
