"""
Fantasy Blueprint  /fantasy/*
Web UI for fantasy draft system.
"""
from typing import Optional

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import current_user, login_required

from app import db
from app.models import FantasyDraft, Tournament, Player, TournamentSeries, SeriesStatus
from app.services import FantasyService, PermissionService, Permission
from app.services.shop_service import ShopService
from app.auth_decorators import requires_permission, admin_required

fantasy_bp = Blueprint("fantasy", __name__)


def _draft_redirect_url(draft: FantasyDraft) -> str:
    """Pick/unpick/cancel actions are shared between the player-facing
    pages and the admin drafts-management page (same routes, keyed off
    draft_id) — sends the user back to whichever page they came from.
    An admin acting on someone ELSE's draft goes back to the admin list
    (they're managing multiple drafts there, not their own). A practice
    draft (see FantasyService module docstring) sends the viewer back to
    the practice tab specifically, via ?tab=practice (see the small tab-
    activation script in fantasy/tournament.html) — otherwise a redirect
    after e.g. cancelling a practice draft would silently land back on
    the paid tab."""
    if current_user.is_authenticated and current_user.is_admin and draft.user_id != current_user.id:
        if draft.tournament_series_id:
            return url_for("fantasy.admin_series_drafts", series_id=draft.tournament_series_id)
        return url_for("fantasy.admin_tournament_drafts", tournament_id=draft.tournament_id)
    tab = {"tab": "practice"} if draft.is_practice else {}
    if draft.tournament_series_id:
        return url_for("fantasy.series_fantasy", series_id=draft.tournament_series_id, **tab)
    return url_for("fantasy.tournament_fantasy", tournament_id=draft.tournament_id, **tab)


def _build_fantasy_mode(tournament: Tournament, series: Optional[TournamentSeries], is_practice: bool) -> dict:
    """
    One tab's worth of data (paid or practice — see FantasyService module
    docstring) for the tournament/series fantasy page: the viewer's own
    draft + available picks, and either one leaderboard/pool (tournament-
    wide) or one card per exclusivity group (series-scoped). The paid and
    practice modes never share a leaderboard, pool, or exclusivity group
    — see FantasyService.get_leaderboard/get_pool_info/_assign_group.
    """
    tournament_id = tournament.id
    series_id = series.id if series else None

    my_draft = None
    available = []
    if current_user.is_authenticated:
        my_draft = FantasyService.get_user_draft(
            current_user.id, tournament_id, series_id, is_practice=is_practice,
        )
        if my_draft and my_draft.status.value == "open":
            available = FantasyService.get_available_picks(
                current_user, tournament_id, series_id, is_practice=is_practice,
            )
    my_group = my_draft.group_number if my_draft else None

    groups = None
    leaderboard = None
    pool_info = None
    if series:
        FantasyService._self_heal_series(series_id)
        group_rows = db.session.query(FantasyDraft.group_number).filter(
            FantasyDraft.tournament_series_id == series_id,
            FantasyDraft.is_practice == is_practice,
        ).distinct().all()
        group_numbers = sorted({g for (g,) in group_rows if g is not None})
        # Legacy drafts predating groups have group_number=None — treat as
        # their own single implicit group so they still show up.
        if any(g is None for (g,) in group_rows):
            group_numbers.append(None)
        groups = [
            {
                "group_number": g,
                "is_mine": g == my_group,
                "leaderboard": FantasyService.get_leaderboard(
                    tournament_id, series_id, group_number=g, is_practice=is_practice,
                ),
                "pool_info": FantasyService.get_pool_info(
                    tournament_id, series_id, group_number=g, is_practice=is_practice,
                ),
            }
            for g in group_numbers
        ]
        groups.sort(key=lambda row: (not row["is_mine"], row["group_number"] is None, row["group_number"]))
    else:
        leaderboard = FantasyService.get_leaderboard(tournament_id, is_practice=is_practice)
        pool_info = FantasyService.get_pool_info(tournament_id, is_practice=is_practice)

    return {
        "is_practice": is_practice,
        "my_draft": my_draft,
        "my_group": my_group,
        "available": available,
        "groups": groups,
        "leaderboard": leaderboard,
        "pool_info": pool_info,
    }


def _mode_pick_player_ids(ctx: dict) -> set:
    ids = set()
    if ctx["my_draft"]:
        ids.update(p.player_id for p in ctx["my_draft"].picks)
    entry_lists = [ctx["leaderboard"]] if ctx["leaderboard"] is not None else [
        grp["leaderboard"] for grp in (ctx["groups"] or [])
    ]
    for entries in entry_lists:
        for e in entries:
            ids.update(pk["player_id"] for pk in e.picks)
    return ids


@fantasy_bp.route("/")
def index():
    """List all tournaments with fantasy drafts, plus active series
    (game evenings) that can be drafted individually.

    Every enrichment below (pool info / top picks) is ONE cheap query
    keyed off FantasyDraft/FantasyDraftPick counts for that single
    tournament/series (typically single/double digits) — not an iterate-
    -all-history loop. The tournaments list itself is capped so the page
    stays bounded as the club's history grows (see the /titles/nominations
    incident: a per-card computation that's cheap today can silently
    become the next O(N) outage once N grows for years).
    """
    tournaments = (
        db.session.query(Tournament)
        .filter(Tournament.status.in_(["pending", "active", "finished"]))
        .order_by(Tournament.created_at.desc())
        .limit(20)
        .all()
    )
    active_series = (
        db.session.query(TournamentSeries)
        .filter_by(status=SeriesStatus.ACTIVE)
        .order_by(TournamentSeries.created_at.desc())
        .all()
    )
    user_drafts = {}
    user_series_drafts = {}
    if current_user.is_authenticated:
        for d in db.session.query(FantasyDraft).filter_by(user_id=current_user.id).all():
            if d.tournament_series_id:
                user_series_drafts[d.tournament_series_id] = d
            else:
                user_drafts[d.tournament_id] = d

    tournament_cards = [
        {
            "tournament": t,
            "pool": FantasyService.get_pool_info(t.id),
            "top_picks": FantasyService.get_top_picks(t.id, limit=3),
        }
        for t in tournaments
    ]
    series_cards = [
        {
            "series": s,
            "pool": FantasyService.get_pool_info(s.series_tournament.tournament_id, s.id),
            "top_picks": FantasyService.get_top_picks(
                s.series_tournament.tournament_id, s.id, limit=3
            ),
            "games_count": len(s.stage.games) if s.stage else 0,
        }
        for s in active_series
    ]

    global_stats = FantasyService.get_global_stats()

    from app.services.nomination_service import NominationService
    top_fantasy = NominationService.get_eternal_ranking("fantasy_oracle", limit=3)
    top_fantasy_ids = [e["player_id"] for e in top_fantasy]
    top_fantasy_players = {
        p.id: p for p in db.session.query(Player).filter(Player.id.in_(top_fantasy_ids)).all()
    } if top_fantasy_ids else {}

    player_ids = set(top_fantasy_ids)
    for card in tournament_cards + series_cards:
        player_ids.update(p["player"].id for p in card["top_picks"])
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "fantasy/index.html",
        tournaments=tournaments,
        user_drafts=user_drafts,
        active_series=active_series,
        user_series_drafts=user_series_drafts,
        tournament_cards=tournament_cards,
        series_cards=series_cards,
        global_stats=global_stats,
        top_fantasy=top_fantasy,
        top_fantasy_players=top_fantasy_players,
        equipped_bulk=equipped_bulk,
    )


@fantasy_bp.route("/tournament/<int:tournament_id>")
def tournament_fantasy(tournament_id: int):
    t = db.session.get(Tournament, tournament_id) or abort(404)

    ctx_paid = _build_fantasy_mode(t, None, is_practice=False)
    ctx_practice = _build_fantasy_mode(t, None, is_practice=True)

    from app.models import TournamentParticipant
    participant_count = db.session.query(TournamentParticipant).filter_by(
        tournament_id=tournament_id
    ).count()
    from app.services.fantasy_service import _allowed_picks
    max_picks = _allowed_picks(participant_count)

    # Персонализация ников для пиков — своих и всех показанных в лидерборде
    # (детализация "кто кого выбрал", см. FantasyLeaderboardEntry.picks) —
    # для обоих режимов сразу, чтобы вкладку можно было переключать без
    # перезагрузки страницы.
    pick_player_ids = _mode_pick_player_ids(ctx_paid) | _mode_pick_player_ids(ctx_practice)
    equipped_bulk = ShopService.get_equipped_bulk(list(pick_player_ids))

    return render_template(
        "fantasy/tournament.html",
        tournament=t,
        series=None,
        modes={"paid": ctx_paid, "practice": ctx_practice},
        entry_cost=ctx_paid["pool_info"]["entry_cost"],
        max_picks=max_picks,
        equipped_bulk=equipped_bulk,
        create_draft_url=url_for("fantasy.create_draft", tournament_id=tournament_id),
        back_url=url_for("fantasy.index"),
    )


@fantasy_bp.route("/tournament/<int:tournament_id>/create", methods=["POST"])
@requires_permission(Permission.CREATE_FANTASY_DRAFT)
def create_draft(tournament_id: int):
    is_practice = request.form.get("is_practice") == "1"
    result = FantasyService.create_draft(current_user, tournament_id, is_practice=is_practice)
    flash(result.message, "success" if result.ok else "danger")
    tab = {"tab": "practice"} if is_practice else {}
    return redirect(url_for("fantasy.tournament_fantasy", tournament_id=tournament_id, **tab))


@fantasy_bp.route("/series/<int:series_id>")
def series_fantasy(series_id: int):
    """Fantasy scoped to one series (game evening) inside a series-tournament
    — own leaderboard/prize pool, scored off that evening's stage rating
    instead of the whole tournament's.

    Exclusivity groups (see FantasyService._assign_group): a draft's picks
    are exclusive only within its own group (own mini-league, own bank),
    but the page shows EVERY group's leaderboard/pool — hiding the others
    would make it look like the rest of the field vanished. The viewer's
    own group (if any) is surfaced first and expanded by default; the
    rest are collapsed but one click away."""
    series = db.session.get(TournamentSeries, series_id) or abort(404)
    tournament = series.series_tournament.tournament

    ctx_paid = _build_fantasy_mode(tournament, series, is_practice=False)
    ctx_practice = _build_fantasy_mode(tournament, series, is_practice=True)

    from app.services.fantasy_service import SERIES_PICKS_PER_DRAFTER
    max_picks = SERIES_PICKS_PER_DRAFTER

    pick_player_ids = _mode_pick_player_ids(ctx_paid) | _mode_pick_player_ids(ctx_practice)
    equipped_bulk = ShopService.get_equipped_bulk(list(pick_player_ids))

    from app.services.economy_service import EconomyService
    entry_cost = EconomyService.get_settings().fantasy_entry_cost

    return render_template(
        "fantasy/tournament.html",
        tournament=tournament,
        series=series,
        modes={"paid": ctx_paid, "practice": ctx_practice},
        entry_cost=entry_cost,
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
    is_practice = request.form.get("is_practice") == "1"
    result = FantasyService.create_draft(current_user, tournament_id, series_id, is_practice=is_practice)
    flash(result.message, "success" if result.ok else "danger")
    tab = {"tab": "practice"} if is_practice else {}
    return redirect(url_for("fantasy.series_fantasy", series_id=series_id, **tab))


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


@fantasy_bp.route("/draft/<int:draft_id>/cancel", methods=["POST"])
@login_required
def cancel_draft(draft_id: int):
    draft = db.session.get(FantasyDraft, draft_id) or abort(404)
    if not PermissionService.can_edit_draft(current_user, draft):
        abort(403)
    # captured before cancel_draft deletes the row — _draft_redirect_url
    # needs a live draft object
    redirect_url = _draft_redirect_url(draft)
    result = FantasyService.cancel_draft(current_user, draft_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(redirect_url)


def _admin_draft_rows(drafts, tournament_id, series_id):
    """Per-draft available-picks list for the admin management page —
    reuses FantasyService.get_available_picks with the DRAFT OWNER (not
    the admin) as the picking user, same as the owner would see on their
    own page. Only computed for OPEN drafts (locked/scored ones show
    read-only, per PermissionService.can_edit_draft/add_pick/remove_pick/
    cancel_draft, which all still gate on status == OPEN even for admins)."""
    rows = []
    for d in drafts:
        available = (
            FantasyService.get_available_picks(d.user, tournament_id, series_id, is_practice=d.is_practice)
            if d.status.value == "open" and d.user else []
        )
        rows.append({"draft": d, "available": available})
    return rows


def _eligible_admin_draft_users(tournament_id, tournament_series_id):
    """Users the admin can open a new draft FOR — same eligibility
    FantasyService.create_draft would itself enforce (not playing in this
    evening/tournament, no existing draft for this tournament/series, has
    a linked player for the entry-fee balance), computed upfront just to
    keep the dropdown free of choices that would only fail on submit.

    For a series with a confirmed roster set, "playing in this evening"
    means THAT roster, not the whole tournament's — see the same fix in
    FantasyService.create_draft (a season/tournament participant who
    simply isn't playing this particular evening must stay eligible)."""
    from app.models import TournamentParticipant
    from app.models.user import User

    # is_practice=False — this dropdown only ever creates PAID drafts (see
    # admin_create_tournament_draft/admin_create_series_draft below), so a
    # user who already has a practice-only draft here must stay eligible.
    existing_user_ids = {
        row[0] for row in db.session.query(FantasyDraft.user_id).filter_by(
            tournament_id=tournament_id, tournament_series_id=tournament_series_id,
            is_practice=False,
        ).all()
    }

    playing_player_ids = None
    if tournament_series_id:
        series = db.session.get(TournamentSeries, tournament_series_id)
        if series and series.confirmed_player_ids is not None:
            playing_player_ids = set(series.confirmed_player_ids)
    if playing_player_ids is None:
        playing_player_ids = {
            row[0] for row in db.session.query(TournamentParticipant.player_id).filter_by(
                tournament_id=tournament_id
            ).all()
        }

    users = (
        db.session.query(User)
        .filter(User.player_id.isnot(None))
        .order_by(User.username)
        .all()
    )
    return [
        u for u in users
        if u.id not in existing_user_ids and u.player_id not in playing_player_ids
    ]


@fantasy_bp.route("/tournament/<int:tournament_id>/admin")
@admin_required
def admin_tournament_drafts(tournament_id: int):
    """Admin-only: view and manage every user's draft for a tournament-wide
    Fantasy pool (add/remove picks, cancel) — for fixing mistakes or
    helping players who can't manage their own draft (e.g. legacy-migration
    login issues). Reuses the same add_pick/remove_pick/cancel_draft routes
    a regular drafter uses, since those already permit admins to act on
    any draft (see PermissionService.can_edit_draft)."""
    t = db.session.get(Tournament, tournament_id) or abort(404)
    drafts = (
        db.session.query(FantasyDraft)
        .filter_by(tournament_id=tournament_id, tournament_series_id=None)
        .order_by(FantasyDraft.created_at)
        .all()
    )
    from app.models import TournamentParticipant
    from app.services.fantasy_service import _allowed_picks
    participant_count = db.session.query(TournamentParticipant).filter_by(
        tournament_id=tournament_id
    ).count()
    max_picks = _allowed_picks(participant_count)

    draft_rows = _admin_draft_rows(drafts, tournament_id, None)
    equipped_bulk = ShopService.get_equipped_bulk(
        [pick.player_id for row in draft_rows for pick in row["draft"].picks]
    )
    eligible_users = _eligible_admin_draft_users(tournament_id, None)
    from app.services.economy_service import EconomyService
    entry_cost = EconomyService.get_settings().fantasy_entry_cost

    return render_template(
        "fantasy/admin_drafts.html",
        tournament=t,
        series=None,
        draft_rows=draft_rows,
        max_picks=max_picks,
        equipped_bulk=equipped_bulk,
        eligible_users=eligible_users,
        entry_cost=entry_cost,
        create_url=url_for("fantasy.admin_create_tournament_draft", tournament_id=tournament_id),
        back_url=url_for("fantasy.tournament_fantasy", tournament_id=tournament_id),
    )


@fantasy_bp.route("/tournament/<int:tournament_id>/admin/create", methods=["POST"])
@admin_required
def admin_create_tournament_draft(tournament_id: int):
    from app.models.user import User

    user_id = request.form.get("user_id", type=int)
    target = db.session.get(User, user_id) if user_id else None
    if not target:
        flash("Пользователь не найден.", "danger")
    else:
        result = FantasyService.create_draft(target, tournament_id)
        flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("fantasy.admin_tournament_drafts", tournament_id=tournament_id))


@fantasy_bp.route("/series/<int:series_id>/admin")
@admin_required
def admin_series_drafts(series_id: int):
    """Admin-only equivalent of admin_tournament_drafts, scoped to one
    series — drafts are grouped by exclusivity group_number (see
    FantasyService._assign_group) so the admin can see at a glance which
    group a mistake needs fixing in."""
    series = db.session.get(TournamentSeries, series_id) or abort(404)
    tournament = series.series_tournament.tournament
    FantasyService._self_heal_series(series_id)

    drafts = (
        db.session.query(FantasyDraft)
        .filter_by(tournament_series_id=series_id)
        .order_by(
            FantasyDraft.is_practice,
            FantasyDraft.group_number.is_(None), FantasyDraft.group_number,
            FantasyDraft.created_at,
        )
        .all()
    )
    from app.services.fantasy_service import SERIES_PICKS_PER_DRAFTER
    max_picks = SERIES_PICKS_PER_DRAFTER

    draft_rows = _admin_draft_rows(drafts, tournament.id, series_id)
    equipped_bulk = ShopService.get_equipped_bulk(
        [pick.player_id for row in draft_rows for pick in row["draft"].picks]
    )
    eligible_users = _eligible_admin_draft_users(tournament.id, series_id)
    from app.services.economy_service import EconomyService
    entry_cost = EconomyService.get_settings().fantasy_entry_cost

    return render_template(
        "fantasy/admin_drafts.html",
        tournament=tournament,
        series=series,
        draft_rows=draft_rows,
        max_picks=max_picks,
        equipped_bulk=equipped_bulk,
        eligible_users=eligible_users,
        entry_cost=entry_cost,
        create_url=url_for("fantasy.admin_create_series_draft", series_id=series_id),
        back_url=url_for("fantasy.series_fantasy", series_id=series_id),
    )


@fantasy_bp.route("/series/<int:series_id>/admin/create", methods=["POST"])
@admin_required
def admin_create_series_draft(series_id: int):
    from app.models.user import User

    series = db.session.get(TournamentSeries, series_id) or abort(404)
    tournament_id = series.series_tournament.tournament_id
    user_id = request.form.get("user_id", type=int)
    target = db.session.get(User, user_id) if user_id else None
    if not target:
        flash("Пользователь не найден.", "danger")
    else:
        result = FantasyService.create_draft(target, tournament_id, series_id)
        flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("fantasy.admin_series_drafts", series_id=series_id))
