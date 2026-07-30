"""
MafiaSpace webhook  /api/mafiaspace/games
==========================================
Входящий вебхук от стороннего сервиса MafiaSpace (см. переписку/докстринг
в ExternalGameImportService) — принимает протокол завершённой игры и
либо сразу создаёт полноценную Game (если все 10 игроков уже сопоставлены
через ExternalPlayerLink), либо откладывает импорт в очередь на ручное
подтверждение админом (/admin/imports).

Авторизация — тот же принцип, что /api/v1/bot/*: серверный токен в
Authorization: Bearer <MAFIASPACE_WEBHOOK_TOKEN>, читается из
current_app.config, до 503 если не настроен на этом деплое.
"""
from flask import Blueprint, current_app, jsonify, request, url_for

from app.services.external_game_import_service import ExternalGameImportService

mafiaspace_bp = Blueprint("mafiaspace", __name__)


def _fail(message: str, code: int = 400):
    return jsonify({"ok": False, "error": message}), code


@mafiaspace_bp.before_request
def _check_webhook_token():
    expected = current_app.config.get("MAFIASPACE_WEBHOOK_TOKEN")
    if not expected:
        return _fail("MafiaSpace webhook не настроен на этом сервере.", 503)
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header[len("Bearer "):] != expected:
        return _fail("Unauthorized", 401)


@mafiaspace_bp.route("/mafiaspace/games", methods=["POST"])
def receive_game():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _fail("Тело запроса должно быть JSON-объектом.")

    external_id = payload.get("external_id")
    if not external_id:
        return _fail("external_id обязателен.")

    outcome = ExternalGameImportService.ingest_webhook_payload(payload)
    if not outcome.ok:
        return _fail(outcome.message)

    if outcome.game:
        external_game_url = url_for("games.game_detail", game_id=outcome.game.id, _external=True)
    else:
        external_game_url = url_for("admin_imports.detail", import_id=outcome.import_row.id, _external=True)

    return jsonify({
        "ok": True,
        "external_id": external_id,
        "external_game_url": external_game_url,
    }), 200
