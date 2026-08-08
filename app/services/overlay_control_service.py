"""
OverlayControlService
======================
Admin-editable live toggles for the /overlay/<tournament_id> stream page —
one OverlayControl row per tournament, lazily created with defaults on
first access (same pattern as EconomyService.get_settings()).
"""
from app import db
from app.models import OverlayControl

STANDINGS_MODES = ("top5", "full", "hidden")
STANDINGS_SCOPES = ("evening", "series")
REVEAL_OVERRIDES = (None, "on", "off")
IDLE_CONTENT_MODES = ("logo", "standings", "last_game", "ticker")


class OverlayControlService:

    @staticmethod
    def get_control(tournament_id: int) -> OverlayControl:
        control = (
            db.session.query(OverlayControl)
            .filter_by(tournament_id=tournament_id)
            .first()
        )
        if not control:
            control = OverlayControl(tournament_id=tournament_id)
            db.session.add(control)
            db.session.commit()
        return control

    @staticmethod
    def toggle_ticker(tournament_id: int) -> OverlayControl:
        control = OverlayControlService.get_control(tournament_id)
        control.show_ticker = not control.show_ticker
        db.session.commit()
        return control

    @staticmethod
    def toggle_seats(tournament_id: int) -> OverlayControl:
        control = OverlayControlService.get_control(tournament_id)
        control.show_seats = not control.show_seats
        db.session.commit()
        return control

    @staticmethod
    def set_standings_mode(tournament_id: int, mode: str) -> OverlayControl:
        if mode not in STANDINGS_MODES:
            mode = "top5"
        control = OverlayControlService.get_control(tournament_id)
        control.standings_mode = mode
        db.session.commit()
        return control

    @staticmethod
    def set_standings_scope(tournament_id: int, scope: str) -> OverlayControl:
        if scope not in STANDINGS_SCOPES:
            scope = "evening"
        control = OverlayControlService.get_control(tournament_id)
        control.standings_scope = scope
        db.session.commit()
        return control

    @staticmethod
    def set_reveal_override(tournament_id: int, value) -> OverlayControl:
        if value not in REVEAL_OVERRIDES:
            value = None
        control = OverlayControlService.get_control(tournament_id)
        control.reveal_override = value
        db.session.commit()
        return control

    @staticmethod
    def set_idle_content(tournament_id: int, mode: str) -> OverlayControl:
        if mode not in IDLE_CONTENT_MODES:
            mode = "logo"
        control = OverlayControlService.get_control(tournament_id)
        control.idle_content = mode
        db.session.commit()
        return control
