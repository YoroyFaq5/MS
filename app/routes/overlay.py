"""
Overlay Blueprint
=================
Public, unauthenticated stream-overlay pages for OBS Browser Source — one
Flask route per broadcast scene (Live-Game, Live-Commentators, Starting
Soon, BRB, Ending), each meant to be added as its OWN Browser Source in
OBS. Scene switching itself (and turning native sources like a webcam
capture on/off) happens in OBS, not on this page — these routes only
decide what to render for whichever scene's URL is currently open, plus a
`/fragment` poll endpoint per "live" scene so admin-controlled panel
visibility (ticker/standings/seats/idle-content) updates without OBS
having to reload the Browser Source. No session/auth in practice (OBS
loads it cold), so all scene routes are intentionally public, same
precedent as `games.api_game`.

Each scene also has a tournament-AGNOSTIC twin under `/overlay/current/*`
that resolves "which tournament" via ActiveBroadcastService instead of a
URL segment — meant to be the URLs actually pasted into OBS, so switching
which tournament is being broadcast (a new event, a different concurrent
tournament) never requires editing OBS sources, just clicking "Сделать
активным" on that tournament's control page. The `/overlay/<id>/*` URLs
still work standalone (e.g. to preview/test one tournament's overlay
without touching what's "active").

Also hosts the admin-only control page (`/overlay/<id>/control` +
its POST actions) that lets an admin/caster show or hide the ticker,
switch the standings between top-5/full/hidden, manually pin the
last-game reveal open or suppressed on top of its normal ~25s auto-timer,
and mark this tournament as the active one for `/overlay/current/*`.
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
from app.services.broadcast_scene_service import BroadcastSceneService
from app.services.active_broadcast_service import ActiveBroadcastService
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


def _build_ctl_sig(control, effective_idle_content: str) -> str:
    """Separate, small change-detection string for admin-controlled panel
    visibility — deliberately NOT folded into `_build_sig()`. That sig
    drives a full DOM replace in overlay.js; this one is diffed on its own
    and applied as a class toggle on the already-existing panel elements,
    so show/hide animates instead of snapping on every unrelated poll.
    effective_idle_content is control.idle_content with the same
    data-availability fallback to 'logo' the template itself uses (see
    _build_live_context) — only meaningful on the Live-Commentators page,
    but harmless to always include (the Live-Game page simply has no
    [data-idle-slot] elements for it to match against)."""
    return (
        f"tk={int(control.show_ticker)}|sh={int(control.show_seats)}"
        f"|sm={control.standings_mode}|rv={control.reveal_override or 'auto'}"
        f"|ic={effective_idle_content}"
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


def _build_live_context(tournament_id: int, layout_mode: str) -> dict:
    """Shared context for the Live-Game and Live-Commentators pages —
    `layout_mode` ("game"/"commentators") picks which of those two this
    call is for. It's a plain call argument rather than an admin-editable
    DB field: since the two layouts are now separate Browser Source URLs
    (see module docstring), which one is showing is simply "which URL is
    open in OBS", not something to also track server-side."""
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

    # Mirrors the has-data checks the template itself uses to gate each
    # idle-hero slot (Live-Commentators only) — see effective_idle_content's
    # docstring in _build_ctl_sig for why this needs to exist in Python too.
    has_facts = bool(
        superlatives.get("mvp") or superlatives.get("don") or superlatives.get("sheriff")
        or superlatives.get("civilian") or superlatives.get("mafia")
        or (hot_streak_rating and hot_streak_count >= 2)
    )
    effective_idle_content = control.idle_content
    if effective_idle_content == "standings" and not (can_show_standings and full_ratings):
        effective_idle_content = "logo"
    elif effective_idle_content == "last_game" and not last_game:
        effective_idle_content = "logo"
    elif effective_idle_content == "ticker" and not has_facts:
        effective_idle_content = "logo"

    return dict(
        tournament=tournament, layout_mode=layout_mode,
        current_game=current_game, current_slots=current_slots,
        last_game=last_game, last_slots=last_slots,
        equipped_bulk=equipped_bulk, ratings_by_pid=ratings_by_pid,
        superlatives=superlatives,
        hot_streak_rating=hot_streak_rating, hot_streak_count=hot_streak_count,
        can_show_standings=can_show_standings, top_ratings=top_ratings,
        full_ratings=full_ratings, standings_title=standings_title,
        control=control,
        effective_idle_content=effective_idle_content,
        sig=_build_sig(tournament, current_game, last_game, standings_scope),
        ctl_sig=_build_ctl_sig(control, effective_idle_content),
    )


def _build_starting_soon_context(tournament_id: int) -> dict:
    tournament = db.session.get(Tournament, tournament_id) or abort(404)
    state = BroadcastSceneService.get(tournament_id)
    started_at = state["timer_started_at"]
    sig = f"td={state['timer_duration']}|ts={started_at if started_at else 0}"
    return dict(tournament=tournament, broadcast_state=state, sig=sig)


# ── Live — Game (default URL, unchanged from before the OBS-scene split) ──

@overlay_bp.route("/<int:tournament_id>")
def overlay_page(tournament_id: int):
    fragment_url = url_for("overlay.overlay_fragment", tournament_id=tournament_id)
    return render_template("overlay/live_page.html", fragment_url=fragment_url, **_build_live_context(tournament_id, "game"))


@overlay_bp.route("/<int:tournament_id>/fragment")
def overlay_fragment(tournament_id: int):
    return render_template("overlay/_live_fragment.html", **_build_live_context(tournament_id, "game"))


# ── Live — Commentators ────────────────────────────────────────────────────

@overlay_bp.route("/<int:tournament_id>/commentators")
def overlay_commentators_page(tournament_id: int):
    fragment_url = url_for("overlay.overlay_commentators_fragment", tournament_id=tournament_id)
    return render_template("overlay/commentators_page.html", fragment_url=fragment_url, **_build_live_context(tournament_id, "commentators"))


@overlay_bp.route("/<int:tournament_id>/commentators/fragment")
def overlay_commentators_fragment(tournament_id: int):
    return render_template("overlay/_live_fragment.html", **_build_live_context(tournament_id, "commentators"))


# ── Starting Soon ───────────────────────────────────────────────────────────

@overlay_bp.route("/<int:tournament_id>/starting-soon")
def overlay_starting_soon_page(tournament_id: int):
    fragment_url = url_for("overlay.overlay_starting_soon_fragment", tournament_id=tournament_id)
    return render_template("overlay/starting_soon_page.html", fragment_url=fragment_url, **_build_starting_soon_context(tournament_id))


@overlay_bp.route("/<int:tournament_id>/starting-soon/fragment")
def overlay_starting_soon_fragment(tournament_id: int):
    return render_template("overlay/_starting_soon_fragment.html", **_build_starting_soon_context(tournament_id))


# ── BRB / Ending — static, no live data, no polling ─────────────────────────

@overlay_bp.route("/<int:tournament_id>/brb")
def overlay_brb_page(tournament_id: int):
    tournament = db.session.get(Tournament, tournament_id) or abort(404)
    return render_template("overlay/brb.html", tournament=tournament)


@overlay_bp.route("/<int:tournament_id>/ending")
def overlay_ending_page(tournament_id: int):
    tournament = db.session.get(Tournament, tournament_id) or abort(404)
    return render_template("overlay/ending.html", tournament=tournament)


# ── Tournament-agnostic "current" scenes — the URLs meant to actually go
#    into OBS (see module docstring). Each is a thin wrapper around its
#    /<id>/* twin: resolve the active tournament id, then delegate. ─────────

def _current_or_no_active(build_fn, *args):
    """Resolves the active tournament id and calls build_fn(tournament_id,
    *args); returns None (caller renders the "no active tournament" page)
    if nothing is set yet."""
    tournament_id = ActiveBroadcastService.get_active_tournament_id()
    if tournament_id is None or db.session.get(Tournament, tournament_id) is None:
        return None
    return build_fn(tournament_id, *args)


@overlay_bp.route("/current")
def overlay_current_page():
    ctx = _current_or_no_active(_build_live_context, "game")
    if ctx is None:
        return render_template("overlay/no_active.html")
    return render_template("overlay/live_page.html", fragment_url=url_for("overlay.overlay_current_fragment"), **ctx)


@overlay_bp.route("/current/fragment")
def overlay_current_fragment():
    ctx = _current_or_no_active(_build_live_context, "game")
    if ctx is None:
        abort(404)
    return render_template("overlay/_live_fragment.html", **ctx)


@overlay_bp.route("/current/commentators")
def overlay_current_commentators_page():
    ctx = _current_or_no_active(_build_live_context, "commentators")
    if ctx is None:
        return render_template("overlay/no_active.html")
    return render_template("overlay/commentators_page.html", fragment_url=url_for("overlay.overlay_current_commentators_fragment"), **ctx)


@overlay_bp.route("/current/commentators/fragment")
def overlay_current_commentators_fragment():
    ctx = _current_or_no_active(_build_live_context, "commentators")
    if ctx is None:
        abort(404)
    return render_template("overlay/_live_fragment.html", **ctx)


@overlay_bp.route("/current/starting-soon")
def overlay_current_starting_soon_page():
    ctx = _current_or_no_active(_build_starting_soon_context)
    if ctx is None:
        return render_template("overlay/no_active.html")
    return render_template("overlay/starting_soon_page.html", fragment_url=url_for("overlay.overlay_current_starting_soon_fragment"), **ctx)


@overlay_bp.route("/current/starting-soon/fragment")
def overlay_current_starting_soon_fragment():
    ctx = _current_or_no_active(_build_starting_soon_context)
    if ctx is None:
        abort(404)
    return render_template("overlay/_starting_soon_fragment.html", **ctx)


@overlay_bp.route("/current/brb")
def overlay_current_brb_page():
    tournament_id = ActiveBroadcastService.get_active_tournament_id()
    tournament = db.session.get(Tournament, tournament_id) if tournament_id else None
    if tournament is None:
        return render_template("overlay/no_active.html")
    return render_template("overlay/brb.html", tournament=tournament)


@overlay_bp.route("/current/ending")
def overlay_current_ending_page():
    tournament_id = ActiveBroadcastService.get_active_tournament_id()
    tournament = db.session.get(Tournament, tournament_id) if tournament_id else None
    if tournament is None:
        return render_template("overlay/no_active.html")
    return render_template("overlay/ending.html", tournament=tournament)


# ── Admin control panel ──────────────────────────────────────────────────

@overlay_bp.route("/<int:tournament_id>/control")
@admin_required
def overlay_control(tournament_id: int):
    tournament = db.session.get(Tournament, tournament_id) or abort(404)
    control = OverlayControlService.get_control(tournament_id)
    series_tournament = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()
    is_active_broadcast = ActiveBroadcastService.get_active_tournament_id() == tournament_id
    return render_template(
        "overlay/control.html",
        tournament=tournament,
        control=control,
        series_tournament=series_tournament,
        is_active_broadcast=is_active_broadcast,
    )


@overlay_bp.route("/<int:tournament_id>/control/set-active", methods=["POST"])
@admin_required
def overlay_set_active(tournament_id: int):
    db.session.get(Tournament, tournament_id) or abort(404)
    ActiveBroadcastService.set_active_tournament_id(tournament_id)
    flash("Этот турнир теперь активен для /overlay/current/* — ссылки в OBS менять не нужно.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))


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


@overlay_bp.route("/<int:tournament_id>/control/idle-content", methods=["POST"])
@admin_required
def overlay_set_idle_content(tournament_id: int):
    mode = request.form.get("mode", "logo")
    control = OverlayControlService.set_idle_content(tournament_id, mode)
    labels = {"logo": "Лого турнира", "standings": "Турнирная таблица", "last_game": "Прошлая игра", "ticker": "Интересные факты"}
    flash(f"Экран ожидания (без игры) на сцене Live — Комментаторы: {labels.get(control.idle_content, control.idle_content)}.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))


@overlay_bp.route("/<int:tournament_id>/control/timer", methods=["POST"])
@admin_required
def overlay_start_timer(tournament_id: int):
    try:
        minutes = float(request.form.get("minutes", "15"))
    except ValueError:
        minutes = 15.0
    BroadcastSceneService.start_timer(tournament_id, round(minutes * 60))
    flash(f"Таймер Starting Soon запущен заново: {minutes:g} мин.", "success")
    return redirect(url_for("overlay.overlay_control", tournament_id=tournament_id))
