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
from app.models import Player
from app.services import ProfileService
from app.services.auth_service import AuthService

api_bot_bp = Blueprint("api_bot", __name__)


def _ok(data=None, message: str = "ok") -> tuple:
    return jsonify({"status": "ok", "message": message, "data": data}), 200


def _fail(message: str, code: int = 400) -> tuple:
    return jsonify({"status": "error", "message": message}), code


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


# ── Аккаунт ───────────────────────────────────────────────────────────────────

@api_bot_bp.route("/account/unlink", methods=["POST"])
def account_unlink():
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    result = AuthService.unlink_telegram(player)
    return (_ok(message=result.message) if result.ok else _fail(result.message))
