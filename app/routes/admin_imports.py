"""
Admin: очередь входящих внешних импортов игр (/admin/imports)
===============================================================
Игры от внешних интеграций (сейчас: MafiaSpace), где хотя бы один
игрок не сопоставлен с нашим Player, попадают сюда — админ вручную
сопоставляет ники с реальными игроками (или заводит новых) и
подтверждает импорт. См. app/services/external_game_import_service.py.
"""
import json

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from app import db
from app.models import Player, ExternalGameImport
from app.services.external_game_import_service import ExternalGameImportService
from app.auth_decorators import admin_required

admin_imports_bp = Blueprint("admin_imports", __name__)


def _active_players():
    return db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()


def _get_import_or_404(import_id: int) -> ExternalGameImport:
    return db.session.get(ExternalGameImport, import_id) or abort(404)


@admin_imports_bp.route("/")
@admin_required
def list_imports():
    pending = (
        db.session.query(ExternalGameImport)
        .filter_by(status="pending_review")
        .order_by(ExternalGameImport.created_at.desc())
        .all()
    )
    cards = []
    for row in pending:
        payload = json.loads(row.raw_payload)
        matched, unmatched = ExternalGameImportService.match_players(payload.get("players") or [])
        cards.append({"row": row, "payload": payload, "matched": matched, "unmatched": unmatched})

    resolved = (
        db.session.query(ExternalGameImport)
        .filter(ExternalGameImport.status != "pending_review")
        .order_by(ExternalGameImport.created_at.desc())
        .limit(20)
        .all()
    )

    return render_template("admin_imports/list.html", cards=cards, resolved=resolved)


@admin_imports_bp.route("/<int:import_id>")
@admin_required
def detail(import_id: int):
    row = _get_import_or_404(import_id)
    payload = json.loads(row.raw_payload)
    matched, unmatched = ExternalGameImportService.match_players(payload.get("players") or [])
    return render_template(
        "admin_imports/detail.html",
        row=row, payload=payload, matched=matched, unmatched=unmatched,
        active_players=_active_players(),
    )


@admin_imports_bp.route("/<int:import_id>/resolve", methods=["POST"])
@admin_required
def resolve(import_id: int):
    row = _get_import_or_404(import_id)
    if row.status != "pending_review":
        flash("Этот импорт уже обработан.", "warning")
        return redirect(url_for("admin_imports.list_imports"))

    payload = json.loads(row.raw_payload)
    _, unmatched = ExternalGameImportService.match_players(payload.get("players") or [])

    resolutions = {}
    for p in unmatched:
        seat = p["seat"]
        choice = request.form.get(f"choice_{seat}", "")
        if choice == "new":
            resolutions[seat] = {"create_new": True}
        elif choice.isdigit():
            resolutions[seat] = {"player_id": int(choice)}
        else:
            flash(f"Не выбран игрок для места {seat} («{p['nickname']}»).", "danger")
            return redirect(url_for("admin_imports.detail", import_id=import_id))

    game, error = ExternalGameImportService.resolve_pending_import(row, resolutions)
    if error:
        flash(error, "danger")
        return redirect(url_for("admin_imports.detail", import_id=import_id))

    flash("Игра импортирована и посчитана.", "success")
    return redirect(url_for("games.game_detail", game_id=game.id))


@admin_imports_bp.route("/<int:import_id>/reject", methods=["POST"])
@admin_required
def reject(import_id: int):
    row = _get_import_or_404(import_id)
    row.status = "rejected"
    db.session.commit()
    flash("Импорт отклонён.", "success")
    return redirect(url_for("admin_imports.list_imports"))
