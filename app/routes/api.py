"""
API Blueprint  /api/*
======================
JSON REST API. All business logic delegates to services.
Authentication via session (Flask-Login) — same as web views.
Future: swap to JWT token auth by replacing current_user source.
"""
from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, login_required

from app import db
from app.models import Player, Tournament, FantasyDraft
from app.services import (
    PermissionService, Permission,
    EconomyService,
    FantasyService,
    ProfileService,
    RatingService,
    TournamentService,
    GiftService,
)
from app.services.player_search_service import PlayerSearchService

api_bp = Blueprint("api", __name__)


def _require(permission: Permission):
    """Inline permission check for API handlers."""
    if not PermissionService.can(current_user if current_user.is_authenticated else None, permission):
        abort(403)


def _ok(data=None, message: str = "ok") -> tuple:
    return jsonify({"status": "ok", "message": message, "data": data}), 200


def _fail(message: str, code: int = 400) -> tuple:
    return jsonify({"status": "error", "message": message}), code


# ── Profile ───────────────────────────────────────────────────────────────────

@api_bp.route("/profile")
@login_required
def profile():
    user = current_user
    player = db.session.get(Player, user.player_id) if user.player_id else None
    data = {
        "user_id":    user.id,
        "username":   user.username,
        "is_admin":   user.is_admin,
        "is_player":  user.is_player,
        "player_id":  user.player_id,
        "player":     player.to_dict() if player else None,
    }
    return _ok(data)


@api_bp.route("/profile/stats")
@login_required
def profile_stats():
    if not current_user.player_id:
        return _fail("Профиль не привязан к игроку.", 404)
    stats = ProfileService.get_extended_stats(current_user.player_id)
    if not stats:
        return _fail("Игрок не найден.", 404)
    return _ok(stats.to_dict())


@api_bp.route("/profile/update", methods=["POST"])
@login_required
def profile_update():
    if not current_user.player_id:
        return _fail("Нет привязанного игрока.", 400)
    player = db.session.get(Player, current_user.player_id)
    data = request.get_json(silent=True) or {}
    result = ProfileService.update_profile(
        player,
        nickname=data.get("nickname"),
        bio=data.get("bio"),
        avatar_url=data.get("avatar_url"),
    )
    return (_ok(message=result.message) if result.ok else _fail(result.message))


@api_bp.route("/players/<int:player_id>/h2h/<int:opponent_id>")
def head_to_head(player_id: int, opponent_id: int):
    data = ProfileService.head_to_head(player_id, opponent_id)
    return _ok(data)


@api_bp.route("/players/<int:player_id>/stats")
def player_stats(player_id: int):
    stats = ProfileService.get_extended_stats(player_id)
    if not stats:
        return _fail("Игрок не найден.", 404)
    return _ok(stats.to_dict())


@api_bp.route("/players/<int:player_id>/achievements")
def player_achievements(player_id: int):
    from app.services import AchievementService
    return _ok(AchievementService.get_all_with_unlock_status(player_id))


# ── Players: поиск по нику (форма создания игры) ───────────────────────────────

@api_bp.route("/players/search")
@login_required
def players_search():
    query = request.args.get("q", "")
    results = PlayerSearchService.find_similar_players(query)
    return _ok([p.to_dict() for p in results])


@api_bp.route("/players/quick-create", methods=["POST"])
@login_required
def players_quick_create():
    if not (current_user.is_authenticated and current_user.is_admin):
        abort(403)

    data = request.get_json(silent=True) or {}
    nickname = (data.get("nickname") or "").strip()
    force = bool(data.get("force"))

    if not nickname:
        return _fail("Ник обязателен.")

    if not force:
        duplicates = PlayerSearchService.find_exact_duplicates(nickname)
        if duplicates:
            return jsonify({
                "status": "duplicate_warning",
                "message": f"Похожий игрок уже есть: {', '.join(p.display_name for p in duplicates)}.",
                "data": [p.to_dict() for p in duplicates],
            }), 200

    # Проверяем и nickname, и name — Player.name тоже уникален в БД, а тут
    # он всегда = nickname (см. ниже), так что коллизия возможна с обеих сторон.
    existing = db.session.query(Player).filter(
        (Player.nickname == nickname) | (Player.name == nickname)
    ).first()
    if existing:
        return _fail(f"Никнейм «{nickname}» уже занят.")

    # name всегда = nickname — Player.name NOT NULL и unique в БД, а тут
    # игрок создаётся только по нику (без отдельного поля "настоящее имя").
    player = Player(nickname=nickname, name=nickname)
    db.session.add(player)
    db.session.commit()
    EconomyService.grant_welcome_bonus(player)
    return _ok(player.to_dict(), f"Игрок «{nickname}» создан.")


# ── Economy ───────────────────────────────────────────────────────────────────

@api_bp.route("/economy/balance")
@login_required
def economy_balance():
    if not current_user.player_id:
        return _ok({"balance": 0.0, "player_id": None})
    player = db.session.get(Player, current_user.player_id)
    return _ok({
        "balance": EconomyService.get_balance(player),
        "player_id": player.id,
        "player_name": player.display_name,
    })


@api_bp.route("/economy/history")
@login_required
def economy_history():
    if not current_user.player_id:
        return _ok([])
    limit = request.args.get("limit", 30, type=int)
    txs = EconomyService.get_history(current_user.player_id, limit=min(limit, 100))
    return _ok([t.to_dict() for t in txs])


@api_bp.route("/economy/admin/adjust", methods=["POST"])
@login_required
def economy_admin_adjust():
    _require(Permission.ADMIN_ADJUST_COINS)
    data = request.get_json(silent=True) or {}
    player_id = data.get("player_id")
    amount = data.get("amount")
    reason = data.get("reason", "")

    if not player_id or amount is None:
        return _fail("player_id и amount обязательны.")

    player = db.session.get(Player, player_id)
    if not player:
        return _fail("Игрок не найден.", 404)

    result = EconomyService.admin_adjust(player, float(amount), reason)
    return (_ok(message=result.message) if result.ok else _fail(result.message))


# ── Fantasy ───────────────────────────────────────────────────────────────────

@api_bp.route("/fantasy/draft", methods=["POST"])
@login_required
def fantasy_create_draft():
    _require(Permission.CREATE_FANTASY_DRAFT)
    data = request.get_json(silent=True) or {}
    tournament_id = data.get("tournament_id")
    if not tournament_id:
        return _fail("tournament_id обязателен.")

    result = FantasyService.create_draft(current_user, int(tournament_id))
    return (_ok(result.data.to_dict() if result.data else None, result.message)
            if result.ok else _fail(result.message))


@api_bp.route("/fantasy/draft/<int:draft_id>/pick", methods=["POST"])
@login_required
def fantasy_add_pick(draft_id: int):
    data = request.get_json(silent=True) or {}
    player_id = data.get("player_id")
    if not player_id:
        return _fail("player_id обязателен.")

    draft = db.session.get(FantasyDraft, draft_id)
    if not draft:
        return _fail("Драфт не найден.", 404)
    if not PermissionService.can_edit_draft(current_user, draft):
        abort(403)

    result = FantasyService.add_pick(current_user, draft_id, int(player_id))
    return (_ok(result.data.to_dict() if result.data else None, result.message)
            if result.ok else _fail(result.message))


@api_bp.route("/fantasy/draft/<int:draft_id>/pick/<int:player_id>", methods=["DELETE"])
@login_required
def fantasy_remove_pick(draft_id: int, player_id: int):
    draft = db.session.get(FantasyDraft, draft_id)
    if not draft:
        return _fail("Драфт не найден.", 404)
    if not PermissionService.can_edit_draft(current_user, draft):
        abort(403)

    result = FantasyService.remove_pick(current_user, draft_id, player_id)
    return (_ok(message=result.message) if result.ok else _fail(result.message))


@api_bp.route("/fantasy/leaderboard/<int:tournament_id>")
def fantasy_leaderboard(tournament_id: int):
    entries = FantasyService.get_leaderboard(tournament_id)
    return _ok([e.to_dict() for e in entries])


@api_bp.route("/fantasy/my/<int:tournament_id>")
@login_required
def fantasy_my_draft(tournament_id: int):
    draft = FantasyService.get_user_draft(current_user.id, tournament_id)
    if not draft:
        return _fail("У вас нет драфта для этого турнира.", 404)
    return _ok(draft.to_dict())


@api_bp.route("/fantasy/available/<int:tournament_id>")
@login_required
def fantasy_available_picks(tournament_id: int):
    players = FantasyService.get_available_picks(current_user, tournament_id)
    return _ok([{"id": p.id, "name": p.display_name, "elo": p.elo} for p in players])


# ── Permissions ───────────────────────────────────────────────────────────────

@api_bp.route("/permissions/check")
@login_required
def permissions_check():
    perm_name = request.args.get("permission")
    if not perm_name:
        return _fail("permission query param required.")
    try:
        perm = Permission[perm_name.upper()]
    except KeyError:
        return _fail(f"Unknown permission: {perm_name}", 400)

    user = current_user if current_user.is_authenticated else None
    return _ok(PermissionService.check(user, perm))


@api_bp.route("/permissions/all")
@login_required
def permissions_all():
    user = current_user if current_user.is_authenticated else None
    perms = PermissionService.user_permissions(user)
    return _ok([p.name for p in perms])


# ── Ratings (extended) ────────────────────────────────────────────────────────

@api_bp.route("/ratings/global")
def ratings_global():
    ratings = RatingService.get_global_rating()
    return _ok([r.to_dict() for r in ratings])


@api_bp.route("/ratings/year/<int:year>")
def ratings_year(year: int):
    from app.services.season_service import SeasonService
    SeasonService.ensure_year_exists(year)
    ratings = RatingService.get_year_rating(year)
    return _ok([r.to_dict() for r in ratings])


@api_bp.route("/ratings/season/<int:season_id>")
def ratings_season(season_id: int):
    ratings = RatingService.get_season_rating(season_id)
    return _ok([r.to_dict() for r in ratings])


# ── Gifts ────────────────────────────────────────────────────────────────────

@api_bp.route("/gifts/unseen-count")
@login_required
def gifts_unseen_count():
    if not current_user.player_id:
        return _ok({"count": 0})
    return _ok({"count": GiftService.get_unseen_count(current_user.player_id)})
