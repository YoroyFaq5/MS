"""
Migration Blueprint  /migration/*
===================================
Одноразовый Migration API — импорт данных из старой версии приложения.
Вся бизнес-логика — в MigrationService, здесь только HTTP-слой (батч,
аутентификация, конверт ответа), как и во всех остальных Blueprint'ах
проекта.

ВАЖНО: этот blueprint регистрируется только если MIGRATION_API_ENABLED=true
(см. app/__init__.py) — без этой переменной окружения роутов не существует
вообще (404, а не 403). После завершения миграции переменную нужно убрать
из .env — это и есть механизм «только для одноразового импорта».

Аутентификация — отдельный секрет MIGRATION_API_TOKEN (заголовок
Authorization: Bearer ...), не обычная сессия/логин: миграция запускается
внешним скриптом, а не из браузера.
"""
import os

from flask import Blueprint, jsonify, request, abort

from app.services.migration_service import MigrationService

migration_bp = Blueprint("migration", __name__)


def _ok(data=None, message: str = "ok") -> tuple:
    return jsonify({"status": "ok", "message": message, "data": data}), 200


def _fail(message: str, code: int = 400) -> tuple:
    return jsonify({"status": "error", "message": message}), code


def _require_migration_token() -> None:
    """
    Отдельная от обычной сессии авторизация — сверяем секрет из заголовка
    с MIGRATION_API_TOKEN. Не логируем сам токен.
    """
    expected = os.environ.get("MIGRATION_API_TOKEN")
    if not expected:
        # Не должно происходить, если blueprint вообще зарегистрирован
        # (см. app/__init__.py), но проверяем явно — без токена в
        # конфиге любой запрос отклоняется.
        abort(503)

    auth_header = request.headers.get("Authorization", "")
    provided = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    if not provided or provided != expected:
        abort(403)


def _get_items() -> list:
    payload = request.get_json(silent=True) or {}
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        abort(400, description="Тело запроса должно содержать непустой список \"items\".")
    return items


@migration_bp.before_request
def _check_auth():
    _require_migration_token()


# ── Endpoints ────────────────────────────────────────────────────────────────

@migration_bp.route("/players", methods=["POST"])
def import_players():
    items = _get_items()
    batch = MigrationService.import_players(items)
    return _ok(batch.to_dict(), f"Игроки: импортировано {batch.imported}, "
                                 f"пропущено {batch.skipped}, ошибок {batch.failed}.")


@migration_bp.route("/users", methods=["POST"])
def import_users():
    items = _get_items()
    batch = MigrationService.import_users(items)
    return _ok(batch.to_dict(), f"Пользователи: импортировано {batch.imported}, "
                                 f"пропущено {batch.skipped}, ошибок {batch.failed}.")


@migration_bp.route("/games", methods=["POST"])
def import_games():
    items = _get_items()
    batch = MigrationService.import_games(items)
    return _ok(batch.to_dict(), f"Игры: импортировано {batch.imported}, "
                                 f"пропущено {batch.skipped}, ошибок {batch.failed}.")


@migration_bp.route("/gg", methods=["POST"])
def import_gg():
    items = _get_items()
    batch = MigrationService.import_gg(items)
    return _ok(batch.to_dict(), f"GG: импортировано {batch.imported}, "
                                 f"пропущено {batch.skipped}, ошибок {batch.failed}.")
