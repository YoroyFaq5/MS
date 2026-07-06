from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user

from app import db
from app.models import ShopItem, ShopCategory
from app.services import ShopService, PermissionService, Permission
from app.services.shop_service import MIN_BUYOUT_INCREMENT
from app.auth_decorators import requires_permission

shop_bp = Blueprint("shop", __name__)


SORT_OPTIONS = {"rarity_desc", "rarity_asc"}


@shop_bp.route("/")
def list_items():
    category_param = request.args.get("category")
    category = None
    if category_param:
        try:
            category = ShopCategory(category_param)
        except ValueError:
            pass

    sort_param = request.args.get("sort")
    if sort_param not in SORT_OPTIONS:
        sort_param = None

    items = ShopService.list_items(category=category, sort=sort_param)

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
        selected_sort=sort_param,
        affordability=affordability,
        player=player,
    )


@shop_bp.route("/<int:item_id>")
def item_detail(item_id: int):
    item = db.session.get(ShopItem, item_id) or abort(404)
    player = current_user.player if current_user.is_authenticated else None
    validation = ShopService.validate_purchase(player, item) if player else None
    owner_inv = ShopService.get_current_owner(item.id)
    return render_template(
        "shop/detail.html", item=item, player=player, validation=validation,
        owner_inv=owner_inv, min_buyout_increment=MIN_BUYOUT_INCREMENT,
    )


@shop_bp.route("/<int:item_id>/purchase", methods=["POST"])
@requires_permission(Permission.PURCHASE_ITEM)
def purchase_item(item_id: int):
    if not current_user.player_id:
        flash("Для покупок нужен привязанный профиль игрока.", "warning")
        return redirect(url_for("shop.item_detail", item_id=item_id))

    result = ShopService.purchase(current_user.player, item_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("shop.item_detail", item_id=item_id))


@shop_bp.route("/<int:item_id>/buyout", methods=["POST"])
@requires_permission(Permission.PURCHASE_ITEM)
def buyout_item(item_id: int):
    if not current_user.player_id:
        flash("Для перекупа нужен привязанный профиль игрока.", "warning")
        return redirect(url_for("shop.item_detail", item_id=item_id))

    try:
        offer_price = float(request.form.get("offer_price", 0))
    except ValueError:
        flash("Некорректная сумма ставки.", "danger")
        return redirect(url_for("shop.item_detail", item_id=item_id))

    result = ShopService.buyout_item(current_user.player, item_id, offer_price)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("shop.item_detail", item_id=item_id))
