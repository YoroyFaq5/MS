"""
Series Tournaments Blueprint
=============================
Все view-функции — тонкие, вся логика в SeriesTournamentService/
TournamentService. Там, где действие уже существует на обычном турнире
(регистрация участника, активация/завершение турнира), используются
существующие роуты tournaments_bp напрямую — здесь для них новых
эндпоинтов нет.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from app import db
from app.models import Player, TournamentSeries
from app.services import SeriesTournamentService, TournamentService, RatingService
from app.services.rating_service import RoleTournamentStats
from app.services.shop_service import ShopService
from app.auth_decorators import admin_required

series_tournaments_bp = Blueprint("series_tournaments", __name__)


def _get_series_tournament_or_404(series_tournament_id: int):
    st = SeriesTournamentService.get_series_tournament(series_tournament_id)
    return st or abort(404)


def _get_series_or_404(series_id: int) -> TournamentSeries:
    return db.session.get(TournamentSeries, series_id) or abort(404)


# ── Серийный турнир ──────────────────────────────────────────────────────────

@series_tournaments_bp.route("/")
def list_series_tournaments():
    tournaments = SeriesTournamentService.list_series_tournaments()
    return render_template("series_tournaments/list.html", series_tournaments=tournaments)


@series_tournaments_bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_series_tournament():
    if request.method == "POST":
        result = SeriesTournamentService.create_series_tournament(
            name=request.form.get("name", ""),
            description=request.form.get("description", ""),
            is_ranked=bool(request.form.get("is_ranked")),
        )
        if result.ok:
            flash(result.message, "success")
            return redirect(url_for("series_tournaments.series_tournament_detail", series_tournament_id=result.data.id))
        flash(result.message, "danger")

    return render_template("series_tournaments/form.html")


@series_tournaments_bp.route("/<int:series_tournament_id>")
def series_tournament_detail(series_tournament_id: int):
    st = _get_series_tournament_or_404(series_tournament_id)
    overall = SeriesTournamentService.get_overall_leaderboard(series_tournament_id)

    all_players = db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()
    registered_ids = {p.player_id for p in st.tournament.participants}
    available_players = [p for p in all_players if p.id not in registered_ids]

    player_ids = {e.player_id for e in overall[:10]} | registered_ids
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "series_tournaments/detail.html",
        series_tournament=st,
        tournament=st.tournament,
        series_list=sorted(st.series, key=lambda s: s.order),
        overall_top=overall[:10],
        available_players=available_players,
        equipped_bulk=equipped_bulk,
    )


# ── Серии ──────────────────────────────────────────────────────────────────────

@series_tournaments_bp.route("/<int:series_tournament_id>/series/new", methods=["GET", "POST"])
@admin_required
def new_series(series_tournament_id: int):
    st = _get_series_tournament_or_404(series_tournament_id)

    if request.method == "POST":
        series_date_str = request.form.get("series_date", "").strip()
        series_date = None
        if series_date_str:
            from datetime import date
            try:
                series_date = date.fromisoformat(series_date_str)
            except ValueError:
                flash("Неверный формат даты.", "danger")
                return redirect(url_for("series_tournaments.new_series", series_tournament_id=series_tournament_id))

        result = SeriesTournamentService.add_series(
            series_tournament_id, name=request.form.get("name", ""), series_date=series_date,
        )
        flash(result.message, "success" if result.ok else "danger")
        if result.ok:
            return redirect(url_for(
                "series_tournaments.series_detail",
                series_tournament_id=series_tournament_id, series_id=result.data.id,
            ))
        return redirect(url_for("series_tournaments.new_series", series_tournament_id=series_tournament_id))

    return render_template("series_tournaments/series_form.html", series_tournament=st)


@series_tournaments_bp.route("/<int:series_tournament_id>/series/<int:series_id>")
def series_detail(series_tournament_id: int, series_id: int):
    st = _get_series_tournament_or_404(series_tournament_id)
    series = _get_series_or_404(series_id)
    if series.series_tournament_id != series_tournament_id:
        abort(404)

    leaderboard = SeriesTournamentService.get_series_leaderboard(series_id)
    games = sorted(series.stage.games, key=lambda g: g.played_at, reverse=True) if series.stage else []

    tournament_players = sorted(
        (p.player for p in st.tournament.participants if p.player),
        key=lambda pl: pl.name,
    )

    equipped_bulk = ShopService.get_equipped_bulk(
        [r.player_id for r in leaderboard] + [p.id for p in tournament_players]
    )

    # Побед по роли / ПУ / Ci / ЛХ — та же логика, что на общем рейтинге
    # турнира (tournaments.leaderboard), только scoped на stage этой
    # конкретной серии/вечера, + суперлативы серии.
    role_breakdown = (
        RatingService.get_role_breakdown(stage_id=series.stage_id) if series.stage_id else {}
    )
    for r in leaderboard:
        r.role_stats = role_breakdown.get(r.player_id) or RoleTournamentStats()
    superlatives = RatingService.pick_role_superlatives(leaderboard, role_breakdown)

    return render_template(
        "series_tournaments/series_detail.html",
        series_tournament=st,
        tournament=st.tournament,
        series=series,
        leaderboard=leaderboard,
        games=games,
        tournament_players=tournament_players,
        equipped_bulk=equipped_bulk,
        superlatives=superlatives,
    )


@series_tournaments_bp.route("/series/<int:series_id>/finish", methods=["POST"])
@admin_required
def finish_series(series_id: int):
    series = _get_series_or_404(series_id)
    result = SeriesTournamentService.finish_series(series_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for(
        "series_tournaments.series_detail",
        series_tournament_id=series.series_tournament_id, series_id=series_id,
    ))


@series_tournaments_bp.route("/series/<int:series_id>/cancel", methods=["POST"])
@admin_required
def cancel_series(series_id: int):
    series = _get_series_or_404(series_id)
    result = SeriesTournamentService.cancel_series(series_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for(
        "series_tournaments.series_detail",
        series_tournament_id=series.series_tournament_id, series_id=series_id,
    ))


@series_tournaments_bp.route("/series/<int:series_id>/generate-seating", methods=["POST"])
@admin_required
def generate_series_seating(series_id: int):
    """
    Рассадка на конкретный вечер — в отличие от обычной «Следующий раунд»
    (которая всегда берёт ВСЕХ участников турнира), тут админ явно
    отмечает, кто пришёл сегодня, и рассадка строится только для них.
    """
    series = _get_series_or_404(series_id)
    if not series.stage_id:
        flash("У серии нет этапа.", "danger")
        return redirect(url_for(
            "series_tournaments.series_detail",
            series_tournament_id=series.series_tournament_id, series_id=series_id,
        ))

    player_ids = request.form.getlist("player_ids", type=int)
    if len(player_ids) < 10:
        flash(f"Нужно выбрать минимум 10 игроков. Выбрано: {len(player_ids)}.", "danger")
        return redirect(url_for(
            "series_tournaments.series_detail",
            series_tournament_id=series.series_tournament_id, series_id=series_id,
        ))

    result = TournamentService.generate_next_round(series.stage_id, player_ids=player_ids)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for(
        "series_tournaments.series_detail",
        series_tournament_id=series.series_tournament_id, series_id=series_id,
    ))


# ── Лидерборды / статистика игрока ───────────────────────────────────────────

@series_tournaments_bp.route("/<int:series_tournament_id>/leaderboard")
def leaderboard(series_tournament_id: int):
    st = _get_series_tournament_or_404(series_tournament_id)
    overall = SeriesTournamentService.get_overall_leaderboard(series_tournament_id)
    equipped_bulk = ShopService.get_equipped_bulk([e.player_id for e in overall])
    return render_template(
        "series_tournaments/leaderboard.html",
        series_tournament=st, tournament=st.tournament, overall=overall,
        equipped_bulk=equipped_bulk,
    )


@series_tournaments_bp.route("/<int:series_tournament_id>/player/<int:player_id>")
def player_stats(series_tournament_id: int, player_id: int):
    st = _get_series_tournament_or_404(series_tournament_id)
    player = db.session.get(Player, player_id) or abort(404)
    breakdown = SeriesTournamentService.get_player_series_breakdown(series_tournament_id, player_id)
    overall = SeriesTournamentService.get_overall_leaderboard(series_tournament_id)
    overall_entry = next((e for e in overall if e.player_id == player_id), None)
    equipped = ShopService.get_equipped(player_id)

    return render_template(
        "series_tournaments/player_stats.html",
        series_tournament=st, tournament=st.tournament, player=player,
        breakdown=breakdown, overall_entry=overall_entry, equipped=equipped,
    )
