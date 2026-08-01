"""
BroadcastSceneService
======================
Which full-screen broadcast scene (Starting Soon / Live / BRB / Ending) is
currently showing on /overlay/<tournament_id>, plus the Starting Soon
countdown. Deliberately stored as a small per-tournament JSON file under
the Flask instance folder (already gitignored, already used for local
runtime state) — NOT a DB column, and NOT a plain in-memory dict:

  - not a DB column: the project has no real Alembic migration history yet
    (migrations/versions/ is empty — see README.md "Разработка" and
    deploy.sh) so an ALTER TABLE here would need either a hand-rolled
    one-off script run manually against the live DB, or a first-ever
    `flask db migrate` autogenerate with no prior baseline — neither is
    something to do blind without DB access.
  - not a plain module-level dict: production runs multiple Gunicorn/uWSGI
    worker processes, each with its own memory — an admin's click landing
    on worker A would be invisible to a viewer's poll landing on worker B.
    A file on disk is visible to every worker on the same machine.

Each tournament gets its OWN file (not one shared file for all tournaments)
specifically so two different broadcasts being controlled at the same time
can't clobber each other's state via a stale read-modify-write. Writes are
atomic (write to a temp file, then os.replace()) so a poll never reads a
half-written file; a race between two admins clicking the SAME tournament's
buttons at the same instant is still possible (last write wins) but that's
an acceptable, low-stakes trade-off for "which scene is live right now" —
the same trade-off any naive unlocked update would have.
"""
import json
import os
import time
from pathlib import Path

from flask import current_app

SCENES = ("starting_soon", "live", "brb", "ending")
DEFAULT_TIMER_SECONDS = 900


def _default_state() -> dict:
    return {"scene": "live", "timer_duration": DEFAULT_TIMER_SECONDS, "timer_started_at": None}


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
    def set_scene(tournament_id: int, scene: str) -> dict:
        if scene not in SCENES:
            scene = "live"
        state = _load(tournament_id)
        state["scene"] = scene
        _save(tournament_id, state)
        return state

    @staticmethod
    def start_timer(tournament_id: int, duration_seconds: int) -> dict:
        state = _load(tournament_id)
        state["timer_duration"] = max(0, duration_seconds)
        state["timer_started_at"] = time.time()
        _save(tournament_id, state)
        return state
