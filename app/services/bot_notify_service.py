"""
BotNotifyService
=================
Site -> Telegram-bot (MS-TelegramBot) event notifications. Historically a
synchronous HTTP POST straight from the request thread — now a thin
compatibility wrapper around NotifyOutboxService: every call site below
(games.py, achievement_service.py, gift_service.py, ...) is unchanged, but
`send_event`/`notify_player` now enqueue a durable NotifyOutboxEvent row
instead of blocking on the bot's availability. See
app/services/notify_outbox_service.py for the actual delivery/retry logic
and app/models::NotifyOutboxEvent for the accepted trade-offs.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class BotNotifyService:
    @staticmethod
    def send_event(event_type: str, payload: dict) -> bool:
        from app.services.notify_outbox_service import NotifyOutboxService

        event = NotifyOutboxService.enqueue(event_type, payload)
        return event is not None

    @staticmethod
    def notify_player(player_id: int, event_type: str, extra_payload: dict) -> bool:
        """
        Удобный шорткат для всех остальных hook-точек (достижения, титулы,
        перекуп, fantasy, подарки, сезонные награды): резолвит
        Player.telegram_id сам и просто не отправляет ничего, если игрок
        не привязан — вызывающему коду не нужно каждый раз повторять эту
        проверку.
        """
        from app.models import Player
        from app import db

        player = db.session.get(Player, player_id)
        if not player or not player.telegram_id:
            return False
        payload = {"telegram_id": player.telegram_id, **extra_payload}
        return BotNotifyService.send_event(event_type, payload)
