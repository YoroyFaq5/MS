from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from app import db
from app.models import ShopItem, ShopCategory, Rarity, Achievement, AchievementCategory, AchievementTrigger, Player
from app.services import AdminShopService, AchievementService
from app.auth_decorators import admin_required

admin_shop_bp = Blueprint("admin_shop", __name__)


# ── Shop items ────────────────────────────────────────────────────────────────

@admin_shop_bp.route("/")
@admin_required
def list_items():
    items = db.session.query(ShopItem).order_by(ShopItem.category, ShopItem.subcategory, ShopItem.name).all()
    players = db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()
    return render_template("admin_shop/list.html", items=items, players=players)


@admin_shop_bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_item():
    if request.method == "POST":
        try:
            category = ShopCategory(request.form.get("category"))
            rarity = Rarity(request.form.get("rarity", "common"))
            price = float(request.form.get("price", 0))
        except ValueError:
            flash("Некорректные значения формы.", "danger")
            return redirect(url_for("admin_shop.new_item"))

        result = AdminShopService.create_item(
            name=request.form.get("name", ""),
            category=category,
            subcategory=request.form.get("subcategory", ""),
            price=price,
            description=request.form.get("description", ""),
            rarity=rarity,
            image_url=request.form.get("image_url"),
            is_unique_purchase=request.form.get("is_unique_purchase") == "on",
        )
        flash(result.message, "success" if result.ok else "danger")
        if result.ok:
            return redirect(url_for("admin_shop.list_items"))
        return redirect(url_for("admin_shop.new_item"))

    return render_template("admin_shop/form.html", item=None, categories=list(ShopCategory), rarities=list(Rarity))


@admin_shop_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_item(item_id: int):
    item = db.session.get(ShopItem, item_id) or abort(404)

    if request.method == "POST":
        try:
            category = ShopCategory(request.form.get("category"))
            rarity = Rarity(request.form.get("rarity", "common"))
            price = float(request.form.get("price", 0))
        except ValueError:
            flash("Некорректные значения формы.", "danger")
            return redirect(url_for("admin_shop.edit_item", item_id=item_id))

        result = AdminShopService.update_item(
            item_id,
            name=request.form.get("name"),
            category=category,
            subcategory=request.form.get("subcategory"),
            price=price,
            description=request.form.get("description"),
            rarity=rarity,
            image_url=request.form.get("image_url"),
            is_unique_purchase=request.form.get("is_unique_purchase") == "on",
        )
        flash(result.message, "success" if result.ok else "danger")
        return redirect(url_for("admin_shop.list_items"))

    return render_template("admin_shop/form.html", item=item, categories=list(ShopCategory), rarities=list(Rarity))


@admin_shop_bp.route("/<int:item_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_item(item_id: int):
    result = AdminShopService.deactivate_item(item_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_shop.list_items"))


@admin_shop_bp.route("/<int:item_id>/activate", methods=["POST"])
@admin_required
def activate_item(item_id: int):
    result = AdminShopService.activate_item(item_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_shop.list_items"))


@admin_shop_bp.route("/<int:item_id>/grant", methods=["POST"])
@admin_required
def grant_item(item_id: int):
    player_id = request.form.get("player_id", type=int)
    reason = request.form.get("reason", "")
    if not player_id:
        flash("Выберите игрока.", "danger")
        return redirect(url_for("admin_shop.list_items"))

    result = AdminShopService.grant_item(player_id, item_id, reason)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_shop.list_items"))


# ── Achievements ─────────────────────────────────────────────────────────────

@admin_shop_bp.route("/achievements")
@admin_required
def list_achievements():
    achievements = db.session.query(Achievement).order_by(Achievement.category, Achievement.name).all()
    players = db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()
    return render_template("admin_shop/achievements_list.html", achievements=achievements, players=players)


@admin_shop_bp.route("/achievements/new", methods=["GET", "POST"])
@admin_required
def new_achievement():
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        name = request.form.get("name", "").strip()
        if not code or not name:
            flash("Код и название обязательны.", "danger")
            return redirect(url_for("admin_shop.new_achievement"))

        exists = db.session.query(Achievement).filter_by(code=code).first()
        if exists:
            flash(f"Достижение с кодом «{code}» уже существует.", "danger")
            return redirect(url_for("admin_shop.new_achievement"))

        try:
            category = AchievementCategory(request.form.get("category"))
            rarity = Rarity(request.form.get("rarity", "common"))
            trigger = AchievementTrigger(request.form.get("trigger", "manual"))
        except ValueError:
            flash("Некорректные значения формы.", "danger")
            return redirect(url_for("admin_shop.new_achievement"))

        achievement = Achievement(
            code=code,
            name=name,
            description=request.form.get("description", "").strip() or None,
            icon=request.form.get("icon", "").strip() or None,
            category=category,
            rarity=rarity,
            trigger=trigger,
            is_hidden=request.form.get("is_hidden") == "on",
        )
        db.session.add(achievement)
        db.session.commit()
        flash(f"Достижение «{name}» создано.", "success")
        return redirect(url_for("admin_shop.list_achievements"))

    return render_template(
        "admin_shop/achievement_form.html",
        achievement=None,
        categories=list(AchievementCategory),
        rarities=list(Rarity),
        triggers=list(AchievementTrigger),
    )


@admin_shop_bp.route("/achievements/<int:achievement_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_achievement(achievement_id: int):
    achievement = db.session.get(Achievement, achievement_id) or abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Название обязательно.", "danger")
            return redirect(url_for("admin_shop.edit_achievement", achievement_id=achievement_id))

        try:
            achievement.category = AchievementCategory(request.form.get("category"))
            achievement.rarity = Rarity(request.form.get("rarity", "common"))
            achievement.trigger = AchievementTrigger(request.form.get("trigger", "manual"))
        except ValueError:
            flash("Некорректные значения формы.", "danger")
            return redirect(url_for("admin_shop.edit_achievement", achievement_id=achievement_id))

        achievement.name = name
        achievement.description = request.form.get("description", "").strip() or None
        achievement.icon = request.form.get("icon", "").strip() or None
        achievement.is_hidden = request.form.get("is_hidden") == "on"
        achievement.is_active = request.form.get("is_active") == "on"
        db.session.commit()
        flash(f"Достижение «{achievement.name}» обновлено.", "success")
        return redirect(url_for("admin_shop.list_achievements"))

    return render_template(
        "admin_shop/achievement_form.html",
        achievement=achievement,
        categories=list(AchievementCategory),
        rarities=list(Rarity),
        triggers=list(AchievementTrigger),
    )


@admin_shop_bp.route("/achievements/<int:achievement_id>/grant", methods=["POST"])
@admin_required
def grant_achievement(achievement_id: int):
    achievement = db.session.get(Achievement, achievement_id) or abort(404)
    player_id = request.form.get("player_id", type=int)
    reason = request.form.get("reason", "")
    if not player_id:
        flash("Выберите игрока.", "danger")
        return redirect(url_for("admin_shop.list_achievements"))

    result = AchievementService.admin_grant(player_id, achievement.code, reason)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_shop.list_achievements"))
