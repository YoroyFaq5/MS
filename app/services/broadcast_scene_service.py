"""
BroadcastSceneService
======================
The Starting Soon countdown timer for /overlay/<tournament_id>/starting-soon.
Deliberately stored as a small per-tournament JSON file under the Flask
instance folder (already gitignored, already used for local runtime state)
— NOT a DB column, and NOT a plain in-memory dict:

  - not a DB column: the project has no real Alembic migration history yet
    (migrations/versions/ is empty — see README.md "Разработка") so an
    ALTER TABLE here would need either a hand-rolled one-off script run
    manually against the live DB, or a first-ever `flask db migrate`
    autogenerate with no prior baseline — neither is something to do blind
    without DB access.
  - not a plain module-level dict: production runs multiple Gunicorn/uWSGI
    worker processes, each with its own memory — an admin's click landing
    on worker A would be invisible to a viewer's poll landing on worker B.
    A file on disk is visible to every worker on the same machine.

Each tournament gets its OWN file (not one shared file for all tournaments)
specifically so two different broadcasts being controlled at the same time
can't clobber each other's state via a stale read-modify-write. Writes are
atomic (write to a temp file, then os.replace()) so a poll never reads a
half-written file.

Note: which broadcast SCENE is showing (Starting Soon/Live/BRB/Ending) used
to live in this same file, but each scene is now its own Browser Source URL
in OBS (see app/routes/overlay.py's module docstring) — OBS itself is the
source of truth for that, so this service only tracks the timer.
"""
import json
import os
import time
from pathlib import Path

from flask import current_app

DEFAULT_TIMER_SECONDS = 900


def _default_state() -> dict:
    return {"timer_duration": DEFAULT_TIMER_SECONDS, "timer_started_at": None}


def _state_dir() -> Path:
    path = Path(current_app.instance_path) / "broadcast_scenes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _state_path(tournament_id: int) -> Path:
    return _state_dir() / f"{tournament_id}.json"


def _load(tournament_id: int) -> dict:
    path = _state_path(tournament_id)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return _default_state()


def _save(tournament_id: int, state: dict) -> None:
    path = _state_path(tournament_id)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(json.dumps(state), encoding="utf-8")
    os.replace(tmp_path, path)  # atomic on the same filesystem — no torn reads


class BroadcastSceneService:

    @staticmethod
    def get(tournament_id: int) -> dict:
        return _load(tournament_id)

    @staticmethod
    def start_timer(tournament_id: int, duration_seconds: int) -> dict:
        state = _load(tournament_id)
        state["timer_duration"] = max(0, duration_seconds)
        state["timer_started_at"] = time.time()
        _save(tournament_id, state)
        return state
