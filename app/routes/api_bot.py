"""
API Blueprint  /api/v1/bot/*
============================
JSON REST API специально для Telegram-бота (MS-TelegramBot, отдельный
репозиторий/деплой). Отличается от /api/* (app/routes/api.py) авторизацией:
не сессия, а серверный токен бота (Authorization: Bearer
<MAIN_API_SERVICE_TOKEN>) на каждый запрос — бот сам не имеет сессии
пользователя, только знает telegram_id того, кто ему написал. Сайт сам
резолвит telegram_id -> Player через колонку Player.telegram_id (бот эту
связь у себя не хранит, см. AuthService.link_telegram/PROJECT_CONTEXT).

Версионирование (/v1/) — сознательно, в отличие от /api/*, у которого
версии нет вообще: этот слой проектируется с нуля, есть возможность
не повторять тот пробел.
"""
from flask import Blueprint, current_app, jsonify, request

from app import db
from app.models import Player, WinSide
from app.services import ProfileService, RatingService
from app.services.auth_service import AuthService

api_bot_bp = Blueprint("api_bot", __name__)


def _ok(data=None, message: str = "ok") -> tuple:
    return jsonify({"status": "ok", "message": message, "data": data}), 200


def _fail(message: str, code: int = 400) -> tuple:
    return jsonify({"status": "error", "message": message}), code


def _paginate(items: list, page: int, per_page: int) -> dict:
    total = len(items)
    start = (page - 1) * per_page
    return {
        "items": items[start:start + per_page],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page if per_page else 0,
    }


@api_bot_bp.before_request
def _check_service_token():
    expected = current_app.config.get("MAIN_API_SERVICE_TOKEN")
    if not expected:
        return _fail("Bot API не настроен на этом сервере.", 503)
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header[len("Bearer "):] != expected:
        return _fail("Unauthorized", 401)


def _resolve_player(telegram_id: str):
    if not telegram_id:
        return None
    return db.session.query(Player).filter_by(telegram_id=telegram_id).first()


# ── Резолв привязки ──────────────────────────────────────────────────────────

@api_bot_bp.route("/resolve")
def resolve():
    telegram_id = request.args.get("telegram_id", "")
    player = _resolve_player(telegram_id)
    if not player:
        return _ok({"linked": False})
    return _ok({"linked": True, "player_id": player.id, "display_name": player.display_name})


# ── Профиль/статистика ────────────────────────────────────────────────────────

@api_bot_bp.route("/profile")
def profile():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    data = ProfileService.get_profile(player.id)
    if not data:
        return _fail("Игрок не найден.", 404)
    return _ok(data)


@api_bot_bp.route("/stats")
def stats():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    extended = ProfileService.get_statistics(player.id)
    if not extended:
        return _fail("Игрок не найден.", 404)
    return _ok({
        "stats": extended.to_dict(),
        "role_stats": ProfileService.get_role_statistics(player.id),
        "partner_stats": ProfileService.get_partner_statistics(player.id),
        "rivalry_stats": ProfileService.get_rivalry_statistics(player.id),
        "comparison_stats": ProfileService.get_comparison_stats(player.id),
    })


@api_bot_bp.route("/compare")
def compare():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    opponent_id = request.args.get("opponent_id", type=int)
    if not opponent_id:
        return _fail("opponent_id обязателен.")

    result = ProfileService.compare_players(player.id, opponent_id)
    if not result:
        return _fail("Не удалось сравнить — проверьте ID соперника.", 404)
    result = {
        **result,
        "player_a": result["player_a"].to_dict(),
        "player_b": result["player_b"].to_dict(),
    }
    return _ok(result)


# ── Рейтинг ───────────────────────────────────────────────────────────────────

@api_bot_bp.route("/ratings")
def ratings():
    scope = request.args.get("scope", "global")
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)

    if scope == "global":
        ratings_list = RatingService.get_global_rating()
    elif scope == "season":
        season_id = request.args.get("season_id", type=int)
        if not season_id:
            return _fail("season_id обязателен для scope=season.")
        ratings_list = RatingService.get_season_rating(season_id)
    elif scope == "year":
        year = request.args.get("year", type=int)
        if not year:
            return _fail("year обязателен для scope=year.")
        from app.services.season_service import SeasonService
        SeasonService.ensure_year_exists(year)
        ratings_list = RatingService.get_year_rating(year)
    else:
        return _fail("Неверный scope (global|season|year).")

    data = [r.to_dict() for r in ratings_list]
    return _ok(_paginate(data, page, per_page))


# ── История игр ───────────────────────────────────────────────────────────────

@api_bot_bp.route("/history")
def history():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)

    slots = ProfileService.get_game_history(
        player.id, limit=per_page, offset=(page - 1) * per_page,
    )
    items = []
    for s in slots:
        won = (
            (s.is_mafia_side and s.game.win_side == WinSide.MAFIA)
            or (s.is_city_side and s.game.win_side == WinSide.CITY)
        )
        items.append({
            "slot": s.to_dict(),
            "game": {
                "id": s.game.id,
                "played_at": s.game.played_at.isoformat(),
                "win_side": s.game.win_side.value,
            },
            "won": won,
        })
    return _ok({"items": items, "page": page, "per_page": per_page})


# ── Экономика ─────────────────────────────────────────────────────────────────

@api_bot_bp.route("/economy/balance")
def economy_balance():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.economy_service import EconomyService
    return _ok({"balance": EconomyService.get_balance(player)})


@api_bot_bp.route("/economy/history")
def economy_history():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.economy_service import EconomyService
    limit = min(request.args.get("limit", 20, type=int), 100)
    txs = EconomyService.get_history(player.id, limit=limit)
    return _ok([t.to_dict() for t in txs])


# ── Достижения/титулы ─────────────────────────────────────────────────────────

@api_bot_bp.route("/achievements")
def achievements():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    return _ok(ProfileService.get_achievements(player.id))


@api_bot_bp.route("/achievements/<int:achievement_id>/pin", methods=["POST"])
def achievement_pin(achievement_id: int):
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.achievement_service import AchievementService
    result = AchievementService.pin(player.id, achievement_id)
    return (_ok(message=result.message) if result.ok else _fail(result.message))


@api_bot_bp.route("/achievements/<int:achievement_id>/unpin", methods=["POST"])
def achievement_unpin(achievement_id: int):
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.achievement_service import AchievementService
    result = AchievementService.unpin(player.id, achievement_id)
    return (_ok(message=result.message) if result.ok else _fail(result.message))


@api_bot_bp.route("/titles")
def titles():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.title_service import TitleService
    return _ok([t.to_dict() for t in TitleService.list_player_titles(player.id)])


# ── Аккаунт ───────────────────────────────────────────────────────────────────

@api_bot_bp.route("/account/unlink", methods=["POST"])
def account_unlink():
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    result = AuthService.unlink_telegram(player)
    return (_ok(message=result.message) if result.ok else _fail(result.message))
