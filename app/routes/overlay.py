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
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify

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
    at all times. Deliberately NOT where pinned_game_id lives (see
    _build_ctl_sig) — a full DOM replace here would also replay the
    camera frame/broadcast bar/seat strip/ambient-motion entrances, which
    read as "the whole page reloaded" for what should be a small, quiet
    content swap inside one panel."""
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
    [data-idle-slot] elements for it to match against). pg= (pinned_game_id)
    rides along here too: a class toggle alone can't update WHAT the
    last_game slot shows, so overlay.js special-cases a pg change to
    splice in fresh innerHTML for just that one slot from the fragment
    HTML it already re-fetches every poll — see poll()'s pinnedGame
    handling — instead of the full-page replace _build_sig's cg/lg
    changes trigger."""
    return (
        f"tk={int(control.show_ticker)}|sh={int(control.show_seats)}"
        f"|mq={int(control.show_marquee)}"
        f"|sm={control.standings_mode}|rv={control.reveal_override or 'auto'}"
        f"|pg={control.pinned_game_id or 0}"
        f"|ic={effective_idle_content}"
    )


def _finished_games_list(tournament: Tournament) -> list:
    """Newest-first {id, number, round_number} dicts for this tournament's
    finished games — same "Тур №N" ordinal as everywhere else (see
    _build_live_context's game_number_by_id). Backs the "pin a specific
    tour" picker on both /control and the OBS dock."""
    game_number_by_id = {g.id: i + 1 for i, g in enumerate(sorted(tournament.games, key=lambda g: g.id))}
    return [
        {"id": g.id, "number": game_number_by_id[g.id], "round_number": g.round_number}
        for g in sorted(tournament.games, key=lambda g: g.id, reverse=True)
        if g.is_finished
    ]


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

    # "Тур №N" — the same ordinal-within-tournament numbering the site's
    # own games list shows (tournaments.tournament_games: games sorted by
    # id, N = position in that list), NOT game.id. The overlay used to show
    # the raw site-wide game.id, which is a different (and to a viewer,
    # meaningless) number from what the tournament page itself calls this
    # game — confusing side by side. game.id is still used everywhere else
    # here (data-last-finished-id, DB lookups); this is display-only.
    game_number_by_id = {g.id: i + 1 for i, g in enumerate(sorted(tournament.games, key=lambda g: g.id))}
    current_game_number = game_number_by_id.get(current_game.id) if current_game else None
    last_game_number = game_number_by_id.get(last_game.id) if last_game else None

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

    # Admin can pin ANY finished game (not just the auto "most recent") to
    # show in the idle-hero's last_game slot — see
    # OverlayControlService.set_pinned_game. Falls back to last_game/
    # last_slots when nothing's pinned, or the pinned game got deleted, or
    # belongs to a different tournament. SECTION 2's auto-reveal-on-finish
    # panel in the template always uses the real last_game/last_slots
    # above, untouched by this — pinning only affects the idle-hero slot
    # on Live-Commentators.
    pinned_game = (
        db.session.query(Game)
        .filter(Game.id == control.pinned_game_id, Game.tournament_id == tournament_id, Game.is_finished == True)
        .first()
        if control.pinned_game_id else None
    )
    hero_game = pinned_game or last_game
    hero_slots = sorted(hero_game.slots, key=lambda s: s.seat_number) if hero_game else []
    hero_game_number = game_number_by_id.get(hero_game.id) if hero_game else None

    finished_games = _finished_games_list(tournament)

    # Bottom scrolling stats marquee — Live-Commentators only (per the
    # brief: there's no free real estate at the bottom of the Live-Game
    # layout, the seat strip already owns it). Skipped entirely on the
    # other layout so that page doesn't pay for the extra aggregation.
    marquee_stats = (
        RatingService.get_marquee_stats(tournament_id) if layout_mode == "commentators" else None
    )

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

    marquee_entries = (
        marquee_stats.top_total + marquee_stats.top_pu_avg + marquee_stats.top_clean
        + marquee_stats.top_dirty + marquee_stats.top_avg_score + marquee_stats.top_pu_count
        + marquee_stats.best_don + marquee_stats.best_sheriff + marquee_stats.best_civilian
        + marquee_stats.best_mafia
        if marquee_stats else []
    )
    all_player_ids = (
        {s.player_id for s in current_slots}
        | {s.player_id for s in last_slots}
        | {s.player_id for s in hero_slots}
        | {r.player_id for r in full_ratings}
        | {e.rating.player_id for e in marquee_entries}
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
    elif effective_idle_content == "last_game" and not hero_game:
        effective_idle_content = "logo"
    elif effective_idle_content == "ticker" and not has_facts:
        effective_idle_content = "logo"

    return dict(
        tournament=tournament, layout_mode=layout_mode,
        current_game=current_game, current_slots=current_slots,
        current_game_number=current_game_number,
        last_game=last_game, last_slots=last_slots,
        last_game_number=last_game_number,
        hero_game=hero_game, hero_slots=hero_slots, hero_game_number=hero_game_number,
        finished_games=finished_games,
        marquee_stats=marquee_stats,
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
        finished_games=_finished_games_list(tournament),
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


@overlay_bp.route("/<int:tournament_id>/control/marquee", methods=["POST"])
@admin_required
def overlay_toggle_marquee(tournament_id: int):
    control = OverlayControlService.toggle_marquee(tournament_id)
    flash(f"Бегущая строка статистики теперь {'видна 👁' if control.show_marquee else 'скрыта 🙈'}.", "success")
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


@overlay_bp.route("/<int:tournament_id>/control/pinned-game", methods=["POST"])
@admin_required
def overlay_set_pinned_game(tournament_id: int):
    game_id = request.form.get("game_id", type=int)  # absent/empty -> None -> unpin (auto)
    control = OverlayControlService.set_pinned_game(tournament_id, game_id)
    if control.pinned_game_id:
        flash("В панели «Прошлая игра» (Live — Комментаторы) закреплён выбранный тур.", "success")
    else:
        flash("Панель «Прошлая игра» снова показывает последнюю завершённую игру автоматически.", "success")
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


# ── OBS Custom Browser Dock — compact remote, separate from /control ───────
# A second, purpose-built page meant to be pinned as an OBS "Custom Browser
# Dock" (OBS → Docks → Custom Browser Dock), not a replacement for
# /<id>/control above. That page is a full Bootstrap admin page — fine in a
# normal browser tab, cramped and heavy for a ~300px-wide panel glanced at
# constantly during a live show. This reuses the EXACT SAME state layer
# (OverlayControlService / BroadcastSceneService / ActiveBroadcastService —
# no new source of truth, nothing duplicated) through its own thin JSON
# endpoints instead of the classic form-POST-and-redirect ones above, for
# two concrete reasons: those always redirect to `overlay_control` (would
# hijack this page's own navigation on every single click since the dock
# would follow that redirect), and a full page reload per click is a much
# worse feel in a panel meant to be clicked constantly. Every route above
# this comment — including all of /<id>/control/* — is untouched by any of
# this and keeps behaving exactly as before, whether opened as a normal
# page or as someone's existing OBS dock.
def _build_obs_control_state(tournament_id: int):
    """Plain-dict snapshot of everything the dock needs — both the initial
    page render and the polling /state endpoint below return exactly this
    shape, so the page's own JS can just re-run the same "paint state"
    function after every action instead of hand-diffing fields. Deliberately
    NOT `_build_live_context`: that pulls ratings/superlatives/recent-form
    for the actual broadcast, none of which this control surface needs."""
    tournament = db.session.get(Tournament, tournament_id)
    if tournament is None:
        return None
    control = OverlayControlService.get_control(tournament_id)
    series_tournament = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()
    timer_state = BroadcastSceneService.get(tournament_id)

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
    # Same "Тур №N" ordinal as the overlay itself (see _build_live_context) —
    # keeps the number shown on the dock consistent with what's on stream.
    game_number_by_id = {g.id: i + 1 for i, g in enumerate(sorted(tournament.games, key=lambda g: g.id))}

    finished_games = _finished_games_list(tournament)

    return dict(
        tournament_id=tournament.id,
        tournament_name=tournament.name,
        is_active_broadcast=ActiveBroadcastService.get_active_tournament_id() == tournament_id,
        has_series=series_tournament is not None,
        show_ticker=control.show_ticker,
        show_seats=control.show_seats,
        show_marquee=control.show_marquee,
        standings_mode=control.standings_mode,
        standings_scope=control.standings_scope,
        reveal_override=control.reveal_override,
        idle_content=control.idle_content,
        pinned_game_id=control.pinned_game_id,
        finished_games=finished_games,
        hide_standings=tournament.hide_standings,
        timer_duration=timer_state["timer_duration"],
        timer_started_at=timer_state["timer_started_at"],
        has_current_game=current_game is not None,
        current_game_number=game_number_by_id.get(current_game.id) if current_game else None,
        current_round=current_game.round_number if current_game else None,
        has_last_game=last_game is not None,
        last_game_number=game_number_by_id.get(last_game.id) if last_game else None,
    )


def _resolve_obs_control_tournament_id(tournament_id):
    """`tournament_id` is None on every /current/obs-control/* route below
    (see their `defaults={"tournament_id": None}`) — resolves it via
    ActiveBroadcastService instead, same as `_current_or_no_active` does
    for the viewer-facing /overlay/current/* scenes, so the dock can use
    the SAME "paste this URL into OBS once, never touch it again" pattern
    those already have. Returns None if there's genuinely nothing to
    resolve (no active tournament set, or it got deleted)."""
    if tournament_id is not None:
        return tournament_id
    active_id = ActiveBroadcastService.get_active_tournament_id()
    if active_id is None or db.session.get(Tournament, active_id) is None:
        return None
    return active_id


def _obs_control_json_body() -> dict:
    return request.get_json(silent=True) or {}


# Every view below is registered under BOTH a per-tournament URL
# (/<id>/obs-control/...) and a tournament-agnostic one (/current/obs-
# control/..., `defaults={"tournament_id": None}` telling Flask that URL
# has no <tournament_id> segment) — one implementation, exactly like
# overlay_current_page/_current_or_no_active do for the viewer-facing
# scenes above. Which URL a caster puts in OBS is their choice; /current/*
# re-resolves the active tournament on every single request (page load,
# poll, or button click), so it keeps working even if the active
# tournament changes while the dock stays open.

@overlay_bp.route("/<int:tournament_id>/obs-control")
@overlay_bp.route("/current/obs-control", defaults={"tournament_id": None})
@admin_required
def overlay_obs_control(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    is_current = tournament_id is None
    action_base = "/overlay/current/obs-control" if is_current else f"/overlay/{resolved_id}/obs-control"
    state_url = url_for("overlay.overlay_obs_control_state") if is_current \
        else url_for("overlay.overlay_obs_control_state", tournament_id=resolved_id)
    state = _build_obs_control_state(resolved_id) if resolved_id is not None else None
    if not is_current and state is None:
        abort(404)
    return render_template(
        "overlay/obs_control.html",
        state=state, is_current=is_current, tournament_id=resolved_id,
        action_base=action_base, state_url=state_url,
    )


@overlay_bp.route("/<int:tournament_id>/obs-control/state")
@overlay_bp.route("/current/obs-control/state", defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_state(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        if tournament_id is None:
            # A real, expected state for /current/* (nothing marked active
            # yet) — 200 with a flag, NOT an error, so the dock's JS can
            # show "no active tournament" instead of "server unreachable".
            return jsonify({"active": False})
        abort(404)
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/ticker", methods=["POST"])
@overlay_bp.route("/current/obs-control/ticker", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_toggle_ticker(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    OverlayControlService.toggle_ticker(resolved_id)
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/seats", methods=["POST"])
@overlay_bp.route("/current/obs-control/seats", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_toggle_seats(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    OverlayControlService.toggle_seats(resolved_id)
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/marquee", methods=["POST"])
@overlay_bp.route("/current/obs-control/marquee", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_toggle_marquee(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    OverlayControlService.toggle_marquee(resolved_id)
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/standings", methods=["POST"])
@overlay_bp.route("/current/obs-control/standings", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_set_standings_mode(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    OverlayControlService.set_standings_mode(resolved_id, _obs_control_json_body().get("mode", "top5"))
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/standings-scope", methods=["POST"])
@overlay_bp.route("/current/obs-control/standings-scope", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_set_standings_scope(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    OverlayControlService.set_standings_scope(resolved_id, _obs_control_json_body().get("scope", "evening"))
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/reveal", methods=["POST"])
@overlay_bp.route("/current/obs-control/reveal", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_set_reveal(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    OverlayControlService.set_reveal_override(resolved_id, _obs_control_json_body().get("override") or None)
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/idle-content", methods=["POST"])
@overlay_bp.route("/current/obs-control/idle-content", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_set_idle_content(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    OverlayControlService.set_idle_content(resolved_id, _obs_control_json_body().get("mode", "logo"))
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/pinned-game", methods=["POST"])
@overlay_bp.route("/current/obs-control/pinned-game", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_set_pinned_game(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    game_id = _obs_control_json_body().get("game_id")  # None/absent -> unpin (auto)
    OverlayControlService.set_pinned_game(resolved_id, int(game_id) if game_id else None)
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/timer", methods=["POST"])
@overlay_bp.route("/current/obs-control/timer", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_start_timer(tournament_id):
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    try:
        minutes = float(_obs_control_json_body().get("minutes", 15))
    except (TypeError, ValueError):
        minutes = 15.0
    BroadcastSceneService.start_timer(resolved_id, round(minutes * 60))
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/set-active", methods=["POST"])
@overlay_bp.route("/current/obs-control/set-active", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_set_active(tournament_id):
    # The one action that's meaningless on /current/*: there's nothing to
    # "make active" without a concrete id (that's the whole point of this
    # button on the per-tournament dock — picking WHICH tournament
    # /current/* should resolve to next).
    if tournament_id is None:
        abort(400)
    db.session.get(Tournament, tournament_id) or abort(404)
    ActiveBroadcastService.set_active_tournament_id(tournament_id)
    state = _build_obs_control_state(tournament_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/hide-all", methods=["POST"])
@overlay_bp.route("/current/obs-control/hide-all", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_hide_all(tournament_id):
    """Quick action — every viewer-facing panel off at once (ticker, seats,
    standings, the last-game reveal) without touching idle_content or which
    tournament is active. Just a convenience wrapper around the same
    setters every button above already calls individually."""
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    control = OverlayControlService.get_control(resolved_id)
    if control.show_ticker:
        OverlayControlService.toggle_ticker(resolved_id)
    if control.show_seats:
        OverlayControlService.toggle_seats(resolved_id)
    if control.show_marquee:
        OverlayControlService.toggle_marquee(resolved_id)
    OverlayControlService.set_standings_mode(resolved_id, "hidden")
    OverlayControlService.set_reveal_override(resolved_id, "off")
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)


@overlay_bp.route("/<int:tournament_id>/obs-control/reset", methods=["POST"])
@overlay_bp.route("/current/obs-control/reset", methods=["POST"], defaults={"tournament_id": None})
@admin_required
def overlay_obs_control_reset(tournament_id):
    """'Safe state' — the same values a brand-new OverlayControl row starts
    with. The dock's own JS requires an explicit confirm before sending
    this (see obs_control.html) since it undoes manual choices."""
    resolved_id = _resolve_obs_control_tournament_id(tournament_id)
    if resolved_id is None:
        abort(409)
    control = OverlayControlService.get_control(resolved_id)
    if not control.show_ticker:
        OverlayControlService.toggle_ticker(resolved_id)
    if not control.show_seats:
        OverlayControlService.toggle_seats(resolved_id)
    if not control.show_marquee:
        OverlayControlService.toggle_marquee(resolved_id)
    OverlayControlService.set_standings_mode(resolved_id, "top5")
    OverlayControlService.set_reveal_override(resolved_id, None)
    OverlayControlService.set_idle_content(resolved_id, "logo")
    OverlayControlService.set_pinned_game(resolved_id, None)
    state = _build_obs_control_state(resolved_id)
    state["active"] = True
    return jsonify(state)
