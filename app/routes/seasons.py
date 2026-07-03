"""
Seasons Blueprint
=================
Read-only views for players + admin actions (tiebreak, year tournament).
Zero business logic here — all delegated to SeasonService / RatingService.
"""
from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, jsonify
)
from flask_login import current_user

from app import db
from app.models import Season, SeasonStatus
from app.services.season_service import SeasonService
from app.services.rating_service import RatingService
from app.auth_decorators import admin_required

seasons_bp = Blueprint("seasons", __name__)


# ── Current season / year overview ───────────────────────────────────────────

@seasons_bp.route("/")
def index():
    current_year = datetime.now(timezone.utc).year
    # Ensure current year always has seasons
    SeasonService.ensure_year_exists(current_year)

    year = request.args.get("year", current_year, type=int)
    seasons = SeasonService.get_seasons_for_year(year)
    current_season = SeasonService.get_current_season()

    # Available years (all years that have seasons in DB)
    years_with_data = (
        db.session.query(Season.year)
        .distinct()
        .order_by(Season.year.desc())
        .all()
    )
    available_years = [r[0] for r in years_with_data]

    # Year rating
    year_ratings = RatingService.get_year_rating(year)

    return render_template(
        "seasons/index.html",
        seasons=seasons,
        current_season=current_season,
        year=year,
        available_years=available_years,
        year_ratings=year_ratings,
    )


@seasons_bp.route("/<int:season_id>")
def detail(season_id: int):
    season = db.session.get(Season, season_id) or abort(404)

    # Use SeasonRatingEngine (formula: TotalPoints * WR% + GG * 0.2)
    from app.services.season_rating_engine import SeasonRatingEngine
    from app.services.gg_service import GGService
    ratings = SeasonRatingEngine.compute_season_ratings(season_id)

    tiebreak_candidates = (
        SeasonService.get_tiebreak_candidates(season_id)
        if season.status == SeasonStatus.WAITING_TIEBREAK
        else []
    )

    # GG entries for this season (admin panel)
    gg_entries = GGService.get_season_gg(season_id)

    from app.models import Game
    recent_games = (
        db.session.query(Game)
        .filter(Game.season_id == season_id, Game.is_finished == True)
        .order_by(Game.played_at.desc())
        .limit(20)
        .all()
    )

    from app.services import TitleService
    season_nominations = TitleService.get_season_nominations(season_id)

    return render_template(
        "seasons/detail.html",
        season=season,
        ratings=ratings,
        tiebreak_candidates=tiebreak_candidates,
        recent_games=recent_games,
        gg_entries=gg_entries,
        season_nominations=season_nominations,
    )


# ── Admin: close expired seasons manually ─────────────────────────────────────

@seasons_bp.route("/admin/close-expired", methods=["POST"])
@admin_required
def close_expired():
    results = SeasonService.close_expired_seasons()
    if not results:
        flash("Нет завершившихся сезонов для закрытия.", "info")
    else:
        for r in results:
            flash(r.message, "success" if r.ok else "warning")
    return redirect(url_for("seasons.index"))


# ── Admin: resolve tiebreak ───────────────────────────────────────────────────

@seasons_bp.route("/<int:season_id>/tiebreak", methods=["POST"])
@admin_required
def resolve_tiebreak(season_id: int):
    player_id = request.form.get("winner_player_id", type=int)
    if not player_id:
        flash("Выберите победителя.", "danger")
        return redirect(url_for("seasons.detail", season_id=season_id))

    result = SeasonService.resolve_tiebreak(season_id, player_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("seasons.detail", season_id=season_id))


# ── Admin: create year tournament ─────────────────────────────────────────────

@seasons_bp.route("/admin/year-tournament", methods=["POST"])
@admin_required
def create_year_tournament():
    year = request.form.get("year", type=int)
    if not year:
        flash("Укажите год.", "danger")
        return redirect(url_for("seasons.index"))

    result = SeasonService.create_year_tournament(year)
    flash(result.message, "success" if result.ok else "danger")
    if result.ok and result.data:
        return redirect(url_for("tournaments.tournament_detail",
                                tournament_id=result.data.id))
    return redirect(url_for("seasons.index"))


# ── API ───────────────────────────────────────────────────────────────────────

@seasons_bp.route("/api/current")
def api_current():
    season = SeasonService.get_current_season()
    if not season:
        return jsonify({"season": None})
    return jsonify({"season": season.to_dict()})


@seasons_bp.route("/api/<int:year>")
def api_year(year: int):
    seasons = SeasonService.get_seasons_for_year(year)
    return jsonify([s.to_dict() for s in seasons])


@seasons_bp.route("/api/<int:season_id>/ratings")
def api_ratings(season_id: int):
    ratings = RatingService.get_season_rating(season_id)
    return jsonify([r.to_dict() for r in ratings])


@seasons_bp.route("/api/year/<int:year>/ratings")
def api_year_ratings(year: int):
    ratings = RatingService.get_year_rating(year)
    return jsonify([r.to_dict() for r in ratings])


# ── Admin: GG management ──────────────────────────────────────────────────────

@seasons_bp.route("/<int:season_id>/gg/add", methods=["POST"])
@admin_required
def add_gg(season_id: int):
    from app.models import Player
    from app.services.gg_service import GGService
    from flask_login import current_user

    player_id = request.form.get("player_id", type=int)
    value     = request.form.get("value", type=float)
    reason    = request.form.get("reason", "").strip()

    if not player_id or value is None:
        flash("Укажите игрока и значение.", "danger")
        return redirect(url_for("seasons.detail", season_id=season_id))

    player = db.session.get(Player, player_id)
    if not player:
        flash("Игрок не найден.", "danger")
        return redirect(url_for("seasons.detail", season_id=season_id))

    admin_id = current_user.id if current_user.is_authenticated else None
    result = GGService.add_gg(player, season_id, value, reason, admin_id=admin_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("seasons.detail", season_id=season_id))


@seasons_bp.route("/gg/<int:gg_id>/revoke", methods=["POST"])
@admin_required
def revoke_gg(gg_id: int):
    from app.services.gg_service import GGService
    from app.models import GG

    gg = db.session.get(GG, gg_id)
    season_id = gg.season_id if gg else None
    result = GGService.revoke_gg(gg_id)
    flash(result.message, "success" if result.ok else "danger")
    if season_id:
        return redirect(url_for("seasons.detail", season_id=season_id))
    return redirect(url_for("seasons.index"))
