"""
BotNotifyService
=================
Fire-and-forget уведомления сайта -> Telegram-бота (MS-TelegramBot,
отдельный репозиторий/деплой). Никакой очереди, никакого фонового
процесса — обычный синхронный HTTP-вызов в момент события, с коротким
таймаутом и полным перехватом ошибок: недоступность бота НИКОГДА не
должна ломать основной пользовательский флоу (например, завершение
игры), поэтому все методы здесь возвращают bool и не бросают исключения.

Подпись — HMAC-SHA256 тела запроса общим секретом (INCOMING_EVENT_SECRET),
та же схема, что бот проверяет в bot/security.py::verify_event_signature.
Без BOT_EVENTS_URL/INCOMING_EVENT_SECRET в конфиге — событие тихо
логируется и не отправляется (тот же принцип, что TELEGRAM_BOT_TOKEN
для Login Widget: отсутствие переменных выключает фичу, а не роняет сайт).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging

from flask import current_app

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 3.0
READ_TIMEOUT = 5.0


class BotNotifyService:
    @staticmethod
    def send_event(event_type: str, payload: dict) -> bool:
        base_url = current_app.config.get("BOT_EVENTS_URL")
        secret = current_app.config.get("INCOMING_EVENT_SECRET")
        if not base_url or not secret:
            logger.info(
                "BotNotifyService: BOT_EVENTS_URL/INCOMING_EVENT_SECRET не заданы — "
                "событие %s не отправлено (фича выключена).", event_type,
            )
            return False

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

        try:
            import requests

            resp = requests.post(
                f"{base_url.rstrip('/')}/events/{event_type}",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature": signature,
                },
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if resp.status_code >= 400:
                logger.warning(
                    "BotNotifyService: событие %s отклонено ботом, HTTP %s",
                    event_type, resp.status_code,
                )
                return False
            return True
        except Exception:
            logger.exception("BotNotifyService: не удалось отправить событие %s", event_type)
            return False

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
