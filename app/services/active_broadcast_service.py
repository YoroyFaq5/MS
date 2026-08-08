"""
ActiveBroadcastService
========================
Which tournament the tournament-agnostic /overlay/current/* Browser Source
URLs currently point at. Lets a caster add those URLs to OBS ONCE and never
touch them again — switching which tournament is live is just clicking
"Сделать активным" on that tournament's /overlay/<id>/control page, not
re-pasting a new numeric-id URL into every OBS source every event.

File-backed under the instance folder for the same reason as
BroadcastSceneService/OverlayControlService's underlying state: prod runs
multiple Gunicorn/uWSGI worker processes with separate memory, so a plain
module-level variable wouldn't be visible across them, and there's no
Alembic baseline yet to safely add a DB-backed singleton setting. ONE
shared file (not per-tournament, unlike BroadcastSceneService) since
"which tournament is active" is inherently a single global value.
"""
import json
import os
from pathlib import Path

from flask import current_app


def _state_path() -> Path:
    path = Path(current_app.instance_path)
    path.mkdir(parents=True, exist_ok=True)
    return path / "active_broadcast.json"


class ActiveBroadcastService:

    @staticmethod
    def get_active_tournament_id():
        path = _state_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("tournament_id")
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    @staticmethod
    def set_active_tournament_id(tournament_id: int) -> None:
        path = _state_path()
        tmp_path = path.with_name(path.name + ".tmp")
        tmp_path.write_text(json.dumps({"tournament_id": tournament_id}), encoding="utf-8")
        os.replace(tmp_path, path)  # atomic on the same filesystem — no torn reads
