"""
LiveGameControlService
=======================
Backs the overlay live-control panel (app/routes/overlay.py's
/live-control/* routes) — lets an admin mark a player killed/voted-out
and optionally reveal a role while a game is still in progress (never
touches an already-finished game's real results), plus track a
night/day/turn "phase" for context. Every mutation also appends a
GameEvent — an immutable protocol of what was marked, when, and by
whom, meant to outlive any individual click (see GameEvent's own
docstring for the ledger rationale).

Deliberately separate from GameSlot.role/is_eliminated's OTHER meaning
at finish_game time: elimination_type/live_role are purely a live
broadcast aid, never read or written by the final results form.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app import db
from app.models import Game, GameSlot, GameEvent, EliminationType, LivePhase, GameEventType, Role


@dataclass
class LiveControlResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "LiveControlResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "LiveControlResult":
        return cls(ok=False, message=msg)


class LiveGameControlService:

    @staticmethod
    def _record_event(
        game_id: int, event_type: GameEventType, admin_id: Optional[int],
        slot_id: Optional[int] = None, phase: Optional[LivePhase] = None,
        turn_number: Optional[int] = None,
    ) -> GameEvent:
        event = GameEvent(
            game_id=game_id, slot_id=slot_id, event_type=event_type,
            phase=phase, turn_number=turn_number, admin_id=admin_id,
        )
        db.session.add(event)
        return event

    @staticmethod
    def mark_eliminated(slot_id: int, kind: EliminationType, admin_id: Optional[int]) -> LiveControlResult:
        slot = db.session.get(GameSlot, slot_id)
        if not slot:
            return LiveControlResult.fail("Место не найдено.")
        game = slot.game
        if game.is_finished:
            return LiveControlResult.fail("Игра уже завершена — используйте форму итогов.")

        slot.is_eliminated = True
        slot.elimination_type = kind
        LiveGameControlService._record_event(
            game.id, GameEventType(kind.value), admin_id,
            slot_id=slot.id, phase=game.live_phase, turn_number=game.live_turn,
        )
        db.session.commit()
        label = "убит" if kind == EliminationType.KILLED else "выгнан голосованием"
        return LiveControlResult.success(
            f"{slot.player.display_name if slot.player else 'Игрок'} отмечен: {label}.", data=slot
        )

    @staticmethod
    def revive(slot_id: int, admin_id: Optional[int]) -> LiveControlResult:
        slot = db.session.get(GameSlot, slot_id)
        if not slot:
            return LiveControlResult.fail("Место не найдено.")
        game = slot.game
        if game.is_finished:
            return LiveControlResult.fail("Игра уже завершена — используйте форму итогов.")
        if not slot.is_eliminated:
            return LiveControlResult.fail("Этот игрок и так отмечен живым.")

        slot.is_eliminated = False
        slot.elimination_type = None
        LiveGameControlService._record_event(
            game.id, GameEventType.REVIVED, admin_id,
            slot_id=slot.id, phase=game.live_phase, turn_number=game.live_turn,
        )
        db.session.commit()
        return LiveControlResult.success(
            f"{slot.player.display_name if slot.player else 'Игрок'} снова отмечен живым.", data=slot
        )

    @staticmethod
    def reveal_role(slot_id: int, role: Role, admin_id: Optional[int]) -> LiveControlResult:
        slot = db.session.get(GameSlot, slot_id)
        if not slot:
            return LiveControlResult.fail("Место не найдено.")
        game = slot.game
        if game.is_finished:
            return LiveControlResult.fail("Игра уже завершена — используйте форму итогов.")

        slot.live_role = role
        LiveGameControlService._record_event(
            game.id, GameEventType.ROLE_REVEALED, admin_id,
            slot_id=slot.id, phase=game.live_phase, turn_number=game.live_turn,
        )
        db.session.commit()
        return LiveControlResult.success(
            f"Роль {slot.player.display_name if slot.player else 'игрока'} раскрыта.", data=slot
        )

    @staticmethod
    def advance_phase(game_id: int, phase: LivePhase, turn: int, admin_id: Optional[int]) -> LiveControlResult:
        game = db.session.get(Game, game_id)
        if not game:
            return LiveControlResult.fail("Игра не найдена.")
        if game.is_finished:
            return LiveControlResult.fail("Игра уже завершена.")
        if turn < 1:
            return LiveControlResult.fail("Номер хода должен быть не меньше 1.")

        game.live_phase = phase
        game.live_turn = turn
        LiveGameControlService._record_event(
            game.id, GameEventType.PHASE_CHANGED, admin_id, phase=phase, turn_number=turn,
        )
        db.session.commit()
        label = "Ночь" if phase == LivePhase.NIGHT else "День"
        return LiveControlResult.success(f"Фаза: {label} {turn}.", data=game)

    @staticmethod
    def revoke_event(event_id: int, admin_id: Optional[int]) -> LiveControlResult:
        """Мягкая отмена ЗАПИСИ протокола (ошиблись при отметке события) —
        не откатывает текущее состояние слота/игры, чисто аудит-правка
        истории. Чтобы отменить сам факт "убит"/"выгнан" на карточке,
        нужен revive()."""
        event = db.session.get(GameEvent, event_id)
        if not event:
            return LiveControlResult.fail("Событие не найдено.")
        if event.is_revoked:
            return LiveControlResult.fail("Событие уже отменено.")

        event.revoked_at = datetime.now(timezone.utc)
        event.revoked_by_admin_id = admin_id
        db.session.commit()
        return LiveControlResult.success("Запись протокола отменена.", data=event)

    @staticmethod
    def get_state(game_id: int) -> Optional[dict]:
        game = db.session.get(Game, game_id)
        if not game:
            return None
        slots = sorted(game.slots, key=lambda s: s.seat_number)
        events = (
            db.session.query(GameEvent)
            .filter_by(game_id=game_id)
            .order_by(GameEvent.created_at.desc())
            .limit(50)
            .all()
        )
        return {
            "game_id": game.id,
            "is_finished": game.is_finished,
            "live_phase": game.live_phase.value if game.live_phase else None,
            "live_turn": game.live_turn,
            "slots": [
                {
                    "slot_id": s.id,
                    "seat_number": s.seat_number,
                    "player_id": s.player_id,
                    "player_name": s.player.display_name if s.player else "?",
                    "is_eliminated": s.is_eliminated,
                    "elimination_type": s.elimination_type.value if s.elimination_type else None,
                    "live_role": s.live_role.value if s.live_role else None,
                }
                for s in slots
            ],
            "events": [e.to_dict() for e in events],
        }
