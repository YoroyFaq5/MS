from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.models import Title, Player, Season
from app.services import TitleService, NominationService
from app.auth_decorators import admin_required

admin_titles_bp = Blueprint("admin_titles", __name__)


@admin_titles_bp.route("/")
@admin_required
def list_titles():
    titles = db.session.query(Title).order_by(Title.type, Title.name).all()
    holders = {pt.title_id: pt for pt in TitleService.get_current_global_holders()}
    players = db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()
    seasons = db.session.query(Season).order_by(Season.year.desc(), Season.number.desc()).all()
    return render_template(
        "admin_titles/list.html",
        titles=titles, holders=holders, players=players, seasons=seasons,
    )


@admin_titles_bp.route("/grant", methods=["POST"])
@admin_required
def grant():
    from flask_login import current_user

    player_id = request.form.get("player_id", type=int)
    title_id = request.form.get("title_id", type=int)
    reason = request.form.get("reason", "")

    title = db.session.get(Title, title_id)
    if not player_id or not title:
        flash("Выберите игрока и титул.", "danger")
        return redirect(url_for("admin_titles.list_titles"))

    result = TitleService.admin_grant(current_user, player_id, title.code, reason)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_titles.list_titles"))


@admin_titles_bp.route("/<int:player_title_id>/revoke", methods=["POST"])
@admin_required
def revoke(player_title_id: int):
    result = TitleService.admin_revoke(player_title_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_titles.list_titles"))


@admin_titles_bp.route("/recompute-season", methods=["POST"])
@admin_required
def recompute_season():
    season_id = request.form.get("season_id", type=int)
    if not season_id:
        flash("Выберите сезон.", "danger")
        return redirect(url_for("admin_titles.list_titles"))
    result = NominationService.compute_seasonal_role_nominations(season_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_titles.list_titles"))


@admin_titles_bp.route("/recompute-global", methods=["POST"])
@admin_required
def recompute_global():
    result = NominationService.recompute_global_titles()
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("admin_titles.list_titles"))
