"""
Overlay Blueprint
=================
Public, unauthenticated stream-overlay page for OBS Browser Source —
one URL per tournament (`/overlay/<tournament_id>`) showing the current
game's seat strip, an animated last-game-results reveal, a rotating
stats ticker and (privacy-gated) a mini standings table. No session/auth
in practice (OBS loads it cold), so both routes are intentionally public,
same precedent as `games.api_game`.

Also hosts the admin-only control page (`/overlay/<id>/control` +
its POST actions) that lets an admin/caster show or hide the ticker,
switch the standings between top-5/full/hidden, and manually pin the
last-game reveal open or suppressed on top of its normal ~25s auto-timer.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from app import db
from app.models import (
    Game, GameSlot, Player, Tournament, TournamentParticipant,
    SeriesTournament, TournamentSeries,
)
from app.services.rating_service import RatingService, RoleTournamentStats
from app.services.shop_service import ShopService
from app.services.overlay_control_service import OverlayControlService
from app.services.series_tournament_service import SeriesTournamentService
from app.auth_decorators import admin_required

overlay_bp = Blueprint("overlay", __name__)


def _build_sig(tournament: Tournament, current_game, last_game, standings_scope: str) -> str:
    """Cheap change-detection string for the client poller — not a hash,
    never shown to viewers. A new finished game always changes this sig,
    so 'DOM replaced' and 'a game just finished' are the same poll cycle
    in overlay.js (no separate reveal-vs-replace race to handle).
    standings_scope ("evening"/"series", only meaningful for a series
    tournament — see _resolve_series_context) is folded in here rather
    than into _build_ctl_sig: switching which dataset is shown is a rare,
    deliberate admin decision, not something toggled every few seconds
    like standings_mode, so a full redraw on change is an acceptable
    trade-off for not having to keep 2x the standings markup in the DOM
    at all times."""
    if current_game:
        seat_pids = tuple(s.player_id for s in sorted(current_game.slots, key=lambda s: s.seat_number))
        cg_part = f"{current_game.id}:{seat_pids}"
    else:
        cg_part = "none"
    lg_part = str(last_game.id) if last_game else "none"
    return f"cg={cg_part}|lg={lg_part}|hs={int(tournament.hide_standings)}|sc={standings_scope}"


def _build_ctl_sig(control) -> str:
    """Separate, small change-detection string for admin-controlled panel
    visibility — deliberately NOT folded into `_build_sig()`. That sig
    drives a full DOM replace in overlay.js; this one is diffed on its own
    and applied as a class toggle on the already-existing panel elements,
    so show/hide animates instead of snapping on every unrelated poll."""
    return (
        f"tk={int(control.show_ticker)}|sh={int(control.show_seats)}"
        f"|sm={control.standings_mode}|rv={control.reveal_override or 'auto'}"
    )


def _resolve_series_context(tournament_id: int, current_game, last_game):
    """A series tournament (see SeriesTournament/TournamentSeries) is just
    one Tournament row whose evenings are TournamentStage children — not
    separate Tournament rows. Returns (series_tournament, current_series):
    current_series is whichever evening the currently-relevant game (the
    in-progress one, or else the last finished one) belongs to — the
    natural "which evening is this broadcast about right now" answer,
    since a series tournament can technically have more than one evening
    active at once (see SeriesTournamentService), but only one is ever
    actually being played/just finished at a time in practice."""
    series_tournament = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()
    if not series_tournament:
        return None, None
    reference_game = current_game or last_game
    current_series = None
    if reference_game and reference_game.stage_id:
        current_series = (
            db.session.query(TournamentSeries)
            .filter_by(stage_id=reference_game.stage_id)
            .first()
        )
    return series_tournament, current_series


def _build_overlay_context(tournament_id: int) -> dict:
    tournament = db.session.get(Tournament, tournament_id) or abort(404)

    current_game = (
        db.session.query(Game)
        .filter(Game.tournament_id == tournament_id, Game.is_finished == False)
        .order_by(Game.played_at.desc(), Game.id.desc())
        .first()
    )
    last_game = (
        db.session.query(Game)
        .filter(Game.tournament_id == tournament_id, Game.is_finished == True)
        .order_by(Game.played_at.desc(), Game.id.desc())
        .first()
    )

    current_slots = sorted(current_game.slots, key=lambda s: s.seat_number) if current_game else []
    last_slots = sorted(last_game.slots, key=lambda s: s.seat_number) if last_game else []

    # This tournament-wide rating is always computed regardless of series
    # scope: it backs the seat-strip's per-player "score so far" stat and
    # the ticker's superlatives/hot-streak facts (both already effectively
    # whole-series-wide for a series tournament, since Game.tournament_id
    # is shared across all its evenings — no scope toggle needed there).
    player_ratings = RatingService.get_tournament_rating(tournament_id)  # already ranked/sorted
    ratings_by_pid = {r.player_id: r for r in player_ratings}

    role_breakdown = RatingService.get_role_breakdown(tournament_id=tournament_id)
    for r in player_ratings:
        r.role_stats = role_breakdown.get(r.player_id) or RoleTournamentStats()
    superlatives = RatingService.pick_role_superlatives(player_ratings, role_breakdown)

    participant_ids = [
        pid for (pid,) in
        db.session.query(TournamentParticipant.player_id).filter_by(tournament_id=tournament_id).all()
    ]
    recent_form = RatingService.get_recent_form(participant_ids)
    hot_streak_rating, hot_streak_count = None, 0
    for pid, form in recent_form.items():
        if form.streak_won and form.streak_count > hot_streak_count:
            hot_streak_count = form.streak_count
            hot_streak_rating = ratings_by_pid.get(pid)

    control = OverlayControlService.get_control(tournament_id)
    series_tournament, current_series = _resolve_series_context(tournament_id, current_game, last_game)

    # ── Privacy gate ─────────────────────────────────────────────────────
    # Deliberately does NOT call tournaments._can_view_standings /
    # _is_tournament_participant — those let a non-participant ADMIN see
    # hidden standings via their own logged-in session on the main site.
    # This page is a public broadcast surface with no session in practice;
    # every viewer here is treated as anonymous, full stop. This is the
    # ONLY thing that decides whether standings markup exists AT ALL —
    # the admin-controlled standings_mode below only decides which of the
    # two (already-privacy-cleared) panels is the visible one. A series
    # tournament has no privacy flag of its own (SeriesTournament is a
    # thin 1:1 wrapper) — the shared Tournament.hide_standings already
    # governs both scopes uniformly.
    can_show_standings = not tournament.hide_standings

    # Which dataset backs the standings panels — for a plain (non-series)
    # tournament this is just the whole-tournament rating as before. For a
    # series tournament, standings_scope picks between "this evening only"
    # (SeriesTournamentService.get_series_leaderboard, a thin passthrough
    # to RatingService.get_stage_rating — same PlayerRating shape) and
    # "whole series overall" (get_overall_leaderboard — SeriesOverallEntry,
    # which the templates already render fine since they only ever touch
    # .rank/.player_id/.total_score/.display_name, all present on both).
    standings_scope = "evening"
    standings_title = tournament.name
    if series_tournament:
        standings_scope = control.standings_scope
        if standings_scope == "series":
            standings_source = SeriesTournamentService.get_overall_leaderboard(series_tournament.id)
        elif current_series:
            standings_source = SeriesTournamentService.get_series_leaderboard(current_series.id)
            standings_title = current_series.name
        else:
            # Series tournament with no resolvable "current evening" yet
            # (e.g. nothing played this series at all) — fall back to the
            # whole-tournament rating rather than showing nothing.
            standings_source = player_ratings
    else:
        standings_source = player_ratings

    # Both the top-5 and full-table panels are rendered whenever privacy
    # allows it, regardless of the CURRENT standings_mode — visibility
    # between them is a pure CSS class toggle driven by ctl_sig (see
    # overlay.js), not DOM presence, so switching modes can animate
    # instead of panels abruptly appearing/disappearing.
    top_ratings = standings_source[:5] if can_show_standings else []
    full_ratings = standings_source if can_show_standings else []

    all_player_ids = (
        {s.player_id for s in current_slots}
        | {s.player_id for s in last_slots}
        | {r.player_id for r in full_ratings}
    )
    equipped_bulk = ShopService.get_equipped_bulk(list(all_player_ids))

    return dict(
        tournament=tournament,
        current_game=current_game, current_slots=current_slots,
        last_game=last_game, last_slots=last_slots,
        equipped_bulk=equipped_bulk, ratings_by_pid=ratings_by_pid,
        superlatives=superlatives,
        hot_streak_rating=hot_streak_rating, hot_streak_count=hot_streak_count,
        can_show_standings=can_show_standings, top_ratings=top_ratings,
        full_ratings=full_ratings, standings_title=standings_title,
        control=control,
        sig=_build_sig(tournament, current_game, last_game, standings_scope),
        ctl_sig=_build_ctl_sig(control),
    )


@overlay_bp.route("/<int:tournament_id>")
def overlay_page(tournament_id: int):
    return render_template("overlay/page.html", **_build_overlay_context(tournament_id))


@overlay_bp.route("/<int:tournament_id>/fragment")
def overlay_fragment(tournament_id: int):
    return render_template("overlay/_fragment.html", **_build_overlay_context(tournament_id))


# ── Admin control panel ──────────────────────────────────────────────────

@overlay_bp.route("/<int:tournament_id>/control")
@admin_required
def overlay_control(tournament_id: int):
    tournament = db.session.get(Tournament, tournament_id) or abort(404)
    control = OverlayControlService.get_control(tournament_id)
    series_tournament = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()
    return render_template(
        "overlay/control.html",
        tournament=tournament,
        control=control,
        series_tournament=series_tournament,
    )


@overlay_bp.route("/<int:tournament_id>/control/ticker", methods=["POST"])
@admin_required
def overlay_toggle_ticker(tournament_id: int):
    control = OverlayControlService.toggle_ticker(tournament_id)
    flash(f"Тикер статистики теперь {'виден 👁' if control.show_ticker else 'скрыт 🙈'}.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))


@overlay_bp.route("/<int:tournament_id>/control/seats", methods=["POST"])
@admin_required
def overlay_toggle_seats(tournament_id: int):
    control = OverlayControlService.toggle_seats(tournament_id)
    flash(f"Полоса игроков теперь {'видна 👁' if control.show_seats else 'скрыта 🙈'}.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))


@overlay_bp.route("/<int:tournament_id>/control/standings-scope", methods=["POST"])
@admin_required
def overlay_set_standings_scope(tournament_id: int):
    scope = request.form.get("scope", "evening")
    control = OverlayControlService.set_standings_scope(tournament_id, scope)
    labels = {"evening": "эта серия (вечер)", "series": "весь турнир целиком"}
    flash(f"Таблица на оверлее считается по: {labels.get(control.standings_scope, control.standings_scope)}.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))


@overlay_bp.route("/<int:tournament_id>/control/standings", methods=["POST"])
@admin_required
def overlay_set_standings_mode(tournament_id: int):
    mode = request.form.get("mode", "top5")
    control = OverlayControlService.set_standings_mode(tournament_id, mode)
    labels = {"top5": "Топ-5", "full": "Полная таблица", "hidden": "Скрыто"}
    flash(f"Таблица на оверлее: {labels.get(control.standings_mode, control.standings_mode)}.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))


@overlay_bp.route("/<int:tournament_id>/control/reveal", methods=["POST"])
@admin_required
def overlay_set_reveal_override(tournament_id: int):
    override = request.form.get("override") or None
    control = OverlayControlService.set_reveal_override(tournament_id, override)
    labels = {None: "Авто", "on": "Всегда показан", "off": "Скрыт"}
    flash(f"Реванш последней игры: {labels.get(control.reveal_override, control.reveal_override)}.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))
