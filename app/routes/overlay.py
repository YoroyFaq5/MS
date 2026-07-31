"""
Overlay Blueprint
=================
Public, unauthenticated stream-overlay page for OBS Browser Source —
one URL per tournament (`/overlay/<tournament_id>`) showing the current
game's seat strip, an animated last-game-results reveal, a rotating
stats ticker and (privacy-gated) a mini standings table. No session/auth
in practice (OBS loads it cold), so both routes are intentionally public,
same precedent as `games.api_game`.
"""
from flask import Blueprint, render_template, abort

from app import db
from app.models import Game, GameSlot, Player, Tournament, TournamentParticipant
from app.services.rating_service import RatingService, RoleTournamentStats
from app.services.shop_service import ShopService

overlay_bp = Blueprint("overlay", __name__)


def _build_sig(tournament: Tournament, current_game, last_game) -> str:
    """Cheap change-detection string for the client poller — not a hash,
    never shown to viewers. A new finished game always changes this sig,
    so 'DOM replaced' and 'a game just finished' are the same poll cycle
    in overlay.js (no separate reveal-vs-replace race to handle)."""
    if current_game:
        seat_pids = tuple(s.player_id for s in sorted(current_game.slots, key=lambda s: s.seat_number))
        cg_part = f"{current_game.id}:{seat_pids}"
    else:
        cg_part = "none"
    lg_part = str(last_game.id) if last_game else "none"
    return f"cg={cg_part}|lg={lg_part}|hs={int(tournament.hide_standings)}"


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

    # ── Privacy gate ─────────────────────────────────────────────────────
    # Deliberately does NOT call tournaments._can_view_standings /
    # _is_tournament_participant — those let a non-participant ADMIN see
    # hidden standings via their own logged-in session on the main site.
    # This page is a public broadcast surface with no session in practice;
    # every viewer here is treated as anonymous, full stop.
    can_show_standings = not tournament.hide_standings
    top_ratings = player_ratings[:5] if can_show_standings else []

    all_player_ids = (
        {s.player_id for s in current_slots}
        | {s.player_id for s in last_slots}
        | {r.player_id for r in top_ratings}
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
        sig=_build_sig(tournament, current_game, last_game),
    )


@overlay_bp.route("/<int:tournament_id>")
def overlay_page(tournament_id: int):
    return render_template("overlay/page.html", **_build_overlay_context(tournament_id))


@overlay_bp.route("/<int:tournament_id>/fragment")
def overlay_fragment(tournament_id: int):
    return render_template("overlay/_fragment.html", **_build_overlay_context(tournament_id))
