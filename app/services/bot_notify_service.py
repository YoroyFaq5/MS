"""
BotNotifyService
=================
Site -> Telegram-bot (MS-TelegramBot) event notifications. Historically a
synchronous HTTP POST straight from the request thread — now a thin
compatibility wrapper around NotifyOutboxService.

Two call shapes, matching NotifyOutboxService's two staging modes:

- send_event() / notify_player() — the default. These only STAGE the event
  in the caller's current db.session (no commit of their own). Call them
  BEFORE your own db.session.commit() so the notification and the business
  change it describes (a purchase, a gift, an achievement, ...) commit
  together atomically, and both vanish together on rollback.
- send_event_committed() / notify_player_committed() — for the few call
  sites that fire *after* their triggering business operation already
  committed (e.g. a route handler reacting to a service call whose own
  transaction finished earlier in the same request). These open and commit
  a short standalone transaction of their own, and never raise.

See app/services/notify_outbox_service.py for the full contract and
app/models::NotifyOutboxEvent for the schema.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class BotNotifyService:
    @staticmethod
    def send_event(event_type: str, payload: dict) -> bool:
        """Stage the event in the CALLER's current transaction — call this
        BEFORE your own db.session.commit(). Always returns True (staging
        itself doesn't fail short of a caller bug, which propagates rather
        than being swallowed here — see NotifyOutboxService.enqueue)."""
        from app.services.notify_outbox_service import NotifyOutboxService

        NotifyOutboxService.enqueue(event_type, payload)
        return True

    @staticmethod
    def notify_player(player_id: int, event_type: str, extra_payload: dict) -> bool:
        """
        Удобный шорткат для всех остальных hook-точек (достижения, титулы,
        перекуп, fantasy, подарки, сезонные награды): резолвит
        Player.telegram_id сам и просто не отправляет ничего, если игрок
        не привязан — вызывающему коду не нужно каждый раз повторять эту
        проверку. Как и send_event(), только СТЕЙДЖИТ событие — вызывайте
        до своего db.session.commit().
        """
        from app.models import Player
        from app import db

        player = db.session.get(Player, player_id)
        if not player or not player.telegram_id:
            return False
        payload = {"telegram_id": player.telegram_id, **extra_payload}
        return BotNotifyService.send_event(event_type, payload)

    @staticmethod
    def send_event_committed(event_type: str, payload: dict) -> bool:
        """Standalone variant — use ONLY when the triggering business
        operation already committed earlier in the same request and there
        is no live transaction left for the event to ride (see
        NotifyOutboxService.enqueue_and_commit). Never raises."""
        from app.services.notify_outbox_service import NotifyOutboxService

        event = NotifyOutboxService.enqueue_and_commit(event_type, payload)
        return event is not None

    @staticmethod
    def notify_player_committed(player_id: int, event_type: str, extra_payload: dict) -> bool:
        """Standalone/self-committing counterpart to notify_player() — see
        send_event_committed()."""
        from app.models import Player
        from app import db

        player = db.session.get(Player, player_id)
        if not player or not player.telegram_id:
            return False
        payload = {"telegram_id": player.telegram_id, **extra_payload}
        return BotNotifyService.send_event_committed(event_type, payload)
