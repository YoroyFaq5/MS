"""
Fantasy Blueprint  /fantasy/*
Web UI for fantasy draft system.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import current_user, login_required

from app import db
from app.models import FantasyDraft, Tournament, Player, TournamentSeries
from app.services import FantasyService, PermissionService, Permission
from app.services.shop_service import ShopService
from app.auth_decorators import requires_permission

fantasy_bp = Blueprint("fantasy", __name__)


def _draft_redirect_url(draft: FantasyDraft) -> str:
    """Pick/unpick actions are shared between tournament-wide and
    series-scoped drafts (same routes, keyed off draft_id) — this sends
    the user back to whichever page they came from."""
    if draft.tournament_series_id:
        return url_for("fantasy.series_fantasy", series_id=draft.tournament_series_id)
    return url_for("fantasy.tournament_fantasy", tournament_id=draft.tournament_id)


@fantasy_bp.route("/")
def index():
    """List all tournaments with fantasy drafts."""
    tournaments = (
        db.session.query(Tournament)
        .filter(Tournament.status.in_(["pending", "active", "finished"]))
        .order_by(Tournament.created_at.desc())
        .all()
    )
    user_drafts = {}
    if current_user.is_authenticated:
        for d in db.session.query(FantasyDraft).filter_by(user_id=current_user.id).all():
            user_drafts[d.tournament_id] = d
    return render_template(
        "fantasy/index.html",
        tournaments=tournaments,
        user_drafts=user_drafts,
    )


@fantasy_bp.route("/tournament/<int:tournament_id>")
def tournament_fantasy(tournament_id: int):
    t = db.session.get(Tournament, tournament_id) or abort(404)
    leaderboard = FantasyService.get_leaderboard(tournament_id)
    pool_info = FantasyService.get_pool_info(tournament_id)
    my_draft = None
    available = []
    if current_user.is_authenticated:
        my_draft = FantasyService.get_user_draft(current_user.id, tournament_id)
        if my_draft and my_draft.status.value == "open":
            available = FantasyService.get_available_picks(current_user, tournament_id)
    from app.models import TournamentParticipant
    participant_count = db.session.query(TournamentParticipant).filter_by(
        tournament_id=tournament_id
    ).count()
    from app.services.fantasy_service import _allowed_picks
    max_picks = _allowed_picks(participant_count)

    # Персонализация ников — только для реальных Player (пики драфта),
    # не для leaderboard (там User — участники fantasy, другая сущность).
    equipped_bulk = ShopService.get_equipped_bulk(
        [p.player_id for p in my_draft.picks] if my_draft else []
    )

    return render_template(
        "fantasy/tournament.html",
        tournament=t,
        series=None,
        leaderboard=leaderboard,
        pool_info=pool_info,
        my_draft=my_draft,
        available_players=available,
        max_picks=max_picks,
        equipped_bulk=equipped_bulk,
        create_draft_url=url_for("fantasy.create_draft", tournament_id=tournament_id),
        back_url=url_for("fantasy.index"),
    )


@fantasy_bp.route("/tournament/<int:tournament_id>/create", methods=["POST"])
@requires_permission(Permission.CREATE_FANTASY_DRAFT)
def create_draft(tournament_id: int):
    result = FantasyService.create_draft(current_user, tournament_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("fantasy.tournament_fantasy", tournament_id=tournament_id))


@fantasy_bp.route("/series/<int:series_id>")
def series_fantasy(series_id: int):
    """Fantasy scoped to one series (game evening) inside a series-tournament
    — own leaderboard/prize pool, scored off that evening's stage rating
    instead of the whole tournament's."""
    series = db.session.get(TournamentSeries, series_id) or abort(404)
    tournament = series.series_tournament.tournament
    leaderboard = FantasyService.get_leaderboard(tournament.id, series_id)
    pool_info = FantasyService.get_pool_info(tournament.id, series_id)
    my_draft = None
    available = []
    if current_user.is_authenticated:
        my_draft = FantasyService.get_user_draft(current_user.id, tournament.id, series_id)
        if my_draft and my_draft.status.value == "open":
            available = FantasyService.get_available_picks(current_user, tournament.id, series_id)
    from app.models import TournamentParticipant
    participant_count = db.session.query(TournamentParticipant).filter_by(
        tournament_id=tournament.id
    ).count()
    from app.services.fantasy_service import _allowed_picks
    max_picks = _allowed_picks(participant_count)

    equipped_bulk = ShopService.get_equipped_bulk(
        [p.player_id for p in my_draft.picks] if my_draft else []
    )

    return render_template(
        "fantasy/tournament.html",
        tournament=tournament,
        series=series,
        leaderboard=leaderboard,
        pool_info=pool_info,
        my_draft=my_draft,
        available_players=available,
        max_picks=max_picks,
        equipped_bulk=equipped_bulk,
        create_draft_url=url_for("fantasy.create_series_draft", series_id=series_id),
        back_url=url_for(
            "series_tournaments.series_detail",
            series_tournament_id=series.series_tournament_id, series_id=series_id,
        ),
    )


@fantasy_bp.route("/series/<int:series_id>/create", methods=["POST"])
@requires_permission(Permission.CREATE_FANTASY_DRAFT)
def create_series_draft(series_id: int):
    series = db.session.get(TournamentSeries, series_id) or abort(404)
    tournament_id = series.series_tournament.tournament_id
    result = FantasyService.create_draft(current_user, tournament_id, series_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("fantasy.series_fantasy", series_id=series_id))


@fantasy_bp.route("/draft/<int:draft_id>/pick", methods=["POST"])
@login_required
def add_pick(draft_id: int):
    draft = db.session.get(FantasyDraft, draft_id) or abort(404)
    if not PermissionService.can_edit_draft(current_user, draft):
        abort(403)
    player_id = request.form.get("player_id", type=int)
    if not player_id:
        flash("Выберите игрока.", "danger")
        return redirect(_draft_redirect_url(draft))
    result = FantasyService.add_pick(current_user, draft_id, player_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(_draft_redirect_url(draft))


@fantasy_bp.route("/draft/<int:draft_id>/remove/<int:player_id>", methods=["POST"])
@login_required
def remove_pick(draft_id: int, player_id: int):
    draft = db.session.get(FantasyDraft, draft_id) or abort(404)
    if not PermissionService.can_edit_draft(current_user, draft):
        abort(403)
    result = FantasyService.remove_pick(current_user, draft_id, player_id)
    flash(result.message, "success" if result.ok else "info")
    return redirect(_draft_redirect_url(draft))
