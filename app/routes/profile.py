from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import current_user

from app import db
from app.models import Player
from app.services import ProfileService, AchievementService, PermissionService, TitleService, ChartDataService
from app.services.shop_service import ShopService
from app.auth_decorators import login_required

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/")
@login_required
def own_profile():
    if not current_user.player_id:
        flash("Привяжите аккаунт к игроку, чтобы открыть профиль.", "warning")
        return redirect(url_for("auth.link_player_page"))
    return redirect(url_for("profile.view_profile", player_id=current_user.player_id))


@profile_bp.route("/<int:player_id>")
def view_profile(player_id: int):
    profile = ProfileService.get_profile(player_id)
    if not profile:
        abort(404)
    is_own = current_user.is_authenticated and current_user.player_id == player_id
    # Список наград владельца нужен только ему самому — для управления
    # экипировкой прямо на странице профиля.
    own_titles = TitleService.list_player_titles(player_id) if is_own else []

    # Статус привязки Telegram — только владельцу, отдельно от to_dict()
    # (telegram_id намеренно не публикуется в общем JSON/профиле).
    telegram_linked = False
    if is_own:
        player = db.session.get(Player, player_id)
        telegram_linked = bool(player and player.telegram_id)

    return render_template(
        "profile/main.html", profile=profile, player_id=player_id,
        is_own=is_own, own_titles=own_titles,
        telegram_linked=telegram_linked,
        telegram_bot_username=current_app.config.get("TELEGRAM_BOT_USERNAME"),
    )


@profile_bp.route("/<int:player_id>/statistics")
def statistics(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    stats = ProfileService.get_statistics(player_id)
    role_stats = ProfileService.get_role_statistics(player_id)
    partner_stats = ProfileService.get_partner_statistics(player_id)
    rivalry_stats = ProfileService.get_rivalry_statistics(player_id)
    tournament_summary = ProfileService.get_tournament_summary(player_id)
    fantasy_summary = ProfileService.get_fantasy_summary(player_id)
    comparison_stats = ProfileService.get_comparison_stats(player_id)

    # Датасеты для Chart.js — считаются только на этой (тяжёлой) подстранице.
    chart_data = {
        "elo": ChartDataService.get_elo_history(player_id),
        "roles": ChartDataService.get_role_timeline(player_id),
        "streaks": ChartDataService.get_streak_timeline(player_id),
        "role_performance": ChartDataService.get_role_performance(player_id),
        "economy": ChartDataService.get_economy_timeline(player_id),
    }

    # Персонализация — сам игрок страницы + все упомянутые в статистике
    # партнёры/соперники (partner_stats/rivalry_stats — dict-записи с
    # player_id, см. ProfileService.get_partner_statistics).
    other_ids = {
        e["player_id"] for e in list(partner_stats.values()) + list(rivalry_stats.values())
        if isinstance(e, dict) and "player_id" in e
    }
    equipped_bulk = ShopService.get_equipped_bulk(list(other_ids) + [player_id])

    return render_template(
        "profile/statistics.html",
        player=player,
        player_id=player_id,
        stats=stats,
        role_stats=role_stats,
        partner_stats=partner_stats,
        rivalry_stats=rivalry_stats,
        tournament_summary=tournament_summary,
        fantasy_summary=fantasy_summary,
        comparison_stats=comparison_stats,
        chart_data=chart_data,
        equipped_bulk=equipped_bulk,
    )


@profile_bp.route("/compare")
def compare():
    a_id = request.args.get("a", type=int)
    b_id = request.args.get("b", type=int)

    comparison = None
    if a_id and b_id:
        if a_id == b_id:
            flash("Выберите двух разных игроков для сравнения.", "warning")
        else:
            comparison = ProfileService.compare_players(a_id, b_id)
            if not comparison:
                abort(404)

    players = (
        db.session.query(Player)
        .filter_by(is_active=True)
        .order_by(Player.name)
        .all()
    )
    equipped_bulk = ShopService.get_equipped_bulk([a_id, b_id]) if comparison else {}

    return render_template(
        "profile/compare.html",
        players=players,
        a_id=a_id,
        b_id=b_id,
        comparison=comparison,
        equipped_bulk=equipped_bulk,
    )


@profile_bp.route("/<int:player_id>/achievements")
def achievements(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    items = ProfileService.get_achievements(player_id)
    unlocked_count = sum(1 for i in items if i["unlocked"])
    total_count = len(items)
    completion_pct = round(unlocked_count / total_count * 100, 1) if total_count else 0.0
    is_own = current_user.is_authenticated and current_user.player_id == player_id
    equipped = ShopService.get_equipped(player_id)
    return render_template(
        "profile/achievements.html",
        player=player,
        player_id=player_id,
        items=items,
        unlocked_count=unlocked_count,
        total_count=total_count,
        completion_pct=completion_pct,
        is_own=is_own,
        equipped=equipped,
    )


@profile_bp.route("/<int:player_id>/achievements/<int:achievement_id>/pin", methods=["POST"])
@login_required
def pin_achievement(player_id: int, achievement_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    if not PermissionService.can_edit_player(current_user, player):
        abort(403)
    result = AchievementService.pin(player_id, achievement_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.achievements", player_id=player_id))


@profile_bp.route("/<int:player_id>/achievements/<int:achievement_id>/unpin", methods=["POST"])
@login_required
def unpin_achievement(player_id: int, achievement_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    if not PermissionService.can_edit_player(current_user, player):
        abort(403)
    result = AchievementService.unpin(player_id, achievement_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.achievements", player_id=player_id))


@profile_bp.route("/<int:player_id>/customization")
def customization(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    data = ProfileService.get_profile_customization(player_id)
    is_own = current_user.is_authenticated and current_user.player_id == player_id
    equipped = ShopService.get_equipped(player_id)
    return render_template(
        "profile/customization.html",
        player=player,
        player_id=player_id,
        customization=data,
        is_own=is_own,
        equipped=equipped,
    )
