"""
BroadcastSceneService
======================
Which full-screen broadcast scene (Starting Soon / Live / BRB / Ending) is
currently showing on /overlay/<tournament_id>, plus the Starting Soon
countdown. Deliberately IN-MEMORY, not a DB column on OverlayControl —
unlike show_ticker/show_seats/standings_mode (persisted, "how this
tournament's overlay is configured"), this is ephemeral operational state —
"what's on screen right now during this broadcast session", same category
as the ~25s reveal auto-timer already handled client-side in overlay.js.

Why not just add a column: the project currently has no real Alembic
migration history (migrations/versions/ is empty — see README.md
"Разработка" section and deploy.sh's comment), so an ALTER TABLE here would
need either a hand-rolled one-off script run manually against the live DB,
or a first-ever `flask db migrate` autogenerate run against production with
no prior baseline to diff against — neither is something to do blind
without DB access. A restart/redeploy mid-broadcast resets this to 'live',
which is an acceptable trade-off for "which scene is live" (the caster
just clicks the scene button again), not an acceptable one for real
tournament data — hence the DB stays untouched.
"""
import time

SCENES = ("starting_soon", "live", "brb", "ending")
DEFAULT_TIMER_SECONDS = 900

_state: dict[int, dict] = {}


def _get(tournament_id: int) -> dict:
    if tournament_id not in _state:
        _state[tournament_id] = {
            "scene": "live",
            "timer_duration": DEFAULT_TIMER_SECONDS,
            "timer_started_at": None,
        }
    return _state[tournament_id]


class BroadcastSceneService:

    @staticmethod
    def get(tournament_id: int) -> dict:
        return dict(_get(tournament_id))

    @staticmethod
    def set_scene(tournament_id: int, scene: str) -> dict:
        if scene not in SCENES:
            scene = "live"
        state = _get(tournament_id)
        state["scene"] = scene
        return dict(state)

    @staticmethod
    def start_timer(tournament_id: int, duration_seconds: int) -> dict:
        state = _get(tournament_id)
        state["timer_duration"] = max(0, duration_seconds)
        state["timer_started_at"] = time.time()
        return dict(state)
