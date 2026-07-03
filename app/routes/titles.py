from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user

from app import db
from app.models import Title, Player
from app.services import TitleService, NominationService
from app.services.nomination_service import SEASONAL_ROLE_TITLES
from app.services.season_service import SeasonService
from app.auth_decorators import login_required

titles_bp = Blueprint("titles", __name__)


@titles_bp.route("/nominations")
def nominations():
    global_holders = TitleService.get_current_global_holders()

    current_season = SeasonService.get_current_season()
    current_leaders = []
    if current_season:
        preview = NominationService.get_role_leaders_preview(current_season.id)
        role_titles = {
            t.code: t for t in db.session.query(Title).filter(
                Title.code.in_(SEASONAL_ROLE_TITLES.values())
            ).all()
        }
        leader_ids = [pid for pid in preview.values() if pid]
        leader_players = {
            p.id: p for p in db.session.query(Player).filter(Player.id.in_(leader_ids)).all()
        } if leader_ids else {}
        for role, title_code in SEASONAL_ROLE_TITLES.items():
            title = role_titles.get(title_code)
            player_id = preview.get(title_code)
            current_leaders.append({
                "title": title,
                "player": leader_players.get(player_id) if player_id else None,
            })

    history = TitleService.get_seasonal_history()

    return render_template(
        "titles/nominations.html",
        global_holders=global_holders,
        current_season=current_season,
        current_leaders=current_leaders,
        history=history,
    )


@titles_bp.route("/<int:player_title_id>/equip", methods=["POST"])
@login_required
def equip(player_title_id: int):
    if not current_user.player_id:
        flash("Нет привязанного профиля игрока.", "danger")
        return redirect(url_for("titles.nominations"))

    result = TitleService.equip(current_user.player, player_title_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.own_profile"))


@titles_bp.route("/unequip", methods=["POST"])
@login_required
def unequip():
    if not current_user.player_id:
        flash("Нет привязанного профиля игрока.", "danger")
        return redirect(url_for("titles.nominations"))

    result = TitleService.unequip(current_user.player)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.own_profile"))
