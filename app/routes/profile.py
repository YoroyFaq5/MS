from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import current_user

from app import db
from app.models import Player
from app.services import ProfileService, AchievementService, PermissionService, TitleService, ChartDataService
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
    return render_template(
        "profile/main.html", profile=profile, player_id=player_id,
        is_own=is_own, own_titles=own_titles,
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

    # Датасеты для Chart.js — считаются только на этой (тяжёлой) подстранице.
    chart_data = {
        "elo": ChartDataService.get_elo_history(player_id),
        "roles": ChartDataService.get_role_timeline(player_id),
        "streaks": ChartDataService.get_streak_timeline(player_id),
        "role_performance": ChartDataService.get_role_performance(player_id),
        "economy": ChartDataService.get_economy_timeline(player_id),
    }

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
        chart_data=chart_data,
    )


@profile_bp.route("/<int:player_id>/achievements")
def achievements(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    items = ProfileService.get_achievements(player_id)
    unlocked_count = sum(1 for i in items if i["unlocked"])
    total_count = len(items)
    completion_pct = round(unlocked_count / total_count * 100, 1) if total_count else 0.0
    is_own = current_user.is_authenticated and current_user.player_id == player_id
    return render_template(
        "profile/achievements.html",
        player=player,
        player_id=player_id,
        items=items,
        unlocked_count=unlocked_count,
        total_count=total_count,
        completion_pct=completion_pct,
        is_own=is_own,
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
    return render_template(
        "profile/customization.html",
        player=player,
        player_id=player_id,
        customization=data,
        is_own=is_own,
    )
