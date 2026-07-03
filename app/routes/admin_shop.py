from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from app import db
from app.models import ShopItem, ShopCategory, Rarity, Achievement, AchievementCategory, AchievementTrigger, Player
from app.services import AdminShopService, AchievementService
from app.auth_decorators import admin_required

admin_shop_bp = Blueprint("admin_shop", __name__)

# Известные типы персонализации → (category, subcategory, допустимые эффекты).
# "custom" — произвольный товар (мерч и т.п.), category/subcategory берутся
# из формы как раньше, data всегда {}.
PERSONALIZATION_TYPES: dict[str, dict] = {
    "frame":        {"category": "profile_customization", "subcategory": "frame",
                      "effects": ["", "glow", "rainbow"]},
    "background":   {"category": "profile_customization", "subcategory": "background",
                      "effects": []},
    "nick_color":   {"category": "nickname", "subcategory": "nick_color",
                      "effects": ["", "glow"]},
    "nick_gradient": {"category": "nickname", "subcategory": "nick_gradient",
                       "effects": ["", "shimmer", "rainbow"]},
    "nick_prefix":  {"category": "nickname", "subcategory": "nick_prefix",
                      "effects": ["", "bounce", "pulse", "shake"]},
    "nick_suffix":  {"category": "nickname", "subcategory": "nick_suffix",
                      "effects": ["", "bounce", "pulse", "shake"]},
}


def _build_category_subcategory_data(form) -> tuple[ShopCategory, str, dict]:
    """
    Собирает (category, subcategory, data) из формы товара. Для известных
    типов персонализации (frame/background/nick_*) category+subcategory
    жёстко определены типом — так рендеринг (_macros.html/profile/main.html)
    гарантированно находит нужный слот по "category:subcategory". Для
    "custom" (физический товар и т.п.) — свободные category/subcategory,
    как раньше, data всегда пустая.
    """
    ptype = form.get("personalization_type", "custom")
    effect = (form.get("data_effect") or "").strip() or None

    if ptype == "custom":
        category = ShopCategory(form.get("category"))
        subcategory = form.get("subcategory_custom", "").strip()
        return category, subcategory, {}

    spec = PERSONALIZATION_TYPES[ptype]
    category = ShopCategory(spec["category"])
    subcategory = spec["subcategory"]

    if ptype in ("frame", "nick_color"):
        data = {"color": form.get("data_color") or "#C7A552"}
    elif ptype == "background":
        data = {"image_url": form.get("data_image_url", "").strip()}
    elif ptype == "nick_gradient":
        data = {
            "from": form.get("data_from") or "#C7A552",
            "to": form.get("data_to") or "#7B0F0F",
        }
    else:  # nick_prefix / nick_suffix
        data = {"text": form.get("data_text", "").strip()}

    if effect and effect in spec["effects"]:
        data["effect"] = effect
    return category, subcategory, data


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
            category, subcategory, data = _build_category_subcategory_data(request.form)
            rarity = Rarity(request.form.get("rarity", "common"))
            price = float(request.form.get("price", 0))
        except ValueError:
            flash("Некорректные значения формы.", "danger")
            return redirect(url_for("admin_shop.new_item"))

        result = AdminShopService.create_item(
            name=request.form.get("name", ""),
            category=category,
            subcategory=subcategory,
            price=price,
            description=request.form.get("description", ""),
            rarity=rarity,
            image_url=request.form.get("image_url"),
            is_unique_purchase=request.form.get("is_unique_purchase") == "on",
            data=data,
        )
        flash(result.message, "success" if result.ok else "danger")
        if result.ok:
            return redirect(url_for("admin_shop.list_items"))
        return redirect(url_for("admin_shop.new_item"))

    return render_template(
        "admin_shop/form.html", item=None, categories=list(ShopCategory), rarities=list(Rarity),
        initial_type="custom", personalization_types=PERSONALIZATION_TYPES,
    )


@admin_shop_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_item(item_id: int):
    item = db.session.get(ShopItem, item_id) or abort(404)

    if request.method == "POST":
        try:
            category, subcategory, data = _build_category_subcategory_data(request.form)
            rarity = Rarity(request.form.get("rarity", "common"))
            price = float(request.form.get("price", 0))
        except ValueError:
            flash("Некорректные значения формы.", "danger")
            return redirect(url_for("admin_shop.edit_item", item_id=item_id))

        result = AdminShopService.update_item(
            item_id,
            name=request.form.get("name"),
            category=category,
            subcategory=subcategory,
            price=price,
            description=request.form.get("description"),
            rarity=rarity,
            image_url=request.form.get("image_url"),
            is_unique_purchase=request.form.get("is_unique_purchase") == "on",
            data=data,
        )
        flash(result.message, "success" if result.ok else "danger")
        return redirect(url_for("admin_shop.list_items"))

    initial_type = "custom"
    for ptype, spec in PERSONALIZATION_TYPES.items():
        if item.category.value == spec["category"] and item.subcategory == spec["subcategory"]:
            initial_type = ptype
            break

    return render_template(
        "admin_shop/form.html", item=item, categories=list(ShopCategory), rarities=list(Rarity),
        initial_type=initial_type, personalization_types=PERSONALIZATION_TYPES,
    )


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
