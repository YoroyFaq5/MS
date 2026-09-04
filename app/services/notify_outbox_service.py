"""
NotifyOutboxService
====================
Durable delivery for site -> MS-TG notifications. See NotifyOutboxEvent's
docstring (app/models) for the overall design and its explicitly-accepted
limitation (not a fully atomic transactional outbox — enqueue() commits its
own short transaction rather than riding along with the caller's business
transaction). What this DOES fix relative to the old fully-synchronous
BotNotifyService:

- the bot being down/slow no longer blocks or risks the request that
  triggered the notification (finish_game, a purchase, ...) — enqueue() is
  a single fast INSERT;
- a delivery failure is retried with exponential backoff instead of being
  silently dropped after one attempt;
- every attempt is visible (status/attempts/last_error) instead of only a
  log line, and a stuck FAILED event can be manually re-queued.

drain() is safe to run from multiple processes/threads at once: each event
is claimed via an atomic conditional UPDATE (only succeeds if the row is
still PENDING), so two workers racing on the same row never both send it.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask import current_app

from app import db
from app.models import NotifyOutboxEvent, OutboxEventStatus

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 3.0
READ_TIMEOUT = 5.0
BASE_BACKOFF_SECONDS = 20
MAX_BACKOFF_SECONDS = 30 * 60


def _backoff_seconds(attempts: int) -> int:
    return min(BASE_BACKOFF_SECONDS * (2 ** max(0, attempts - 1)), MAX_BACKOFF_SECONDS)


class NotifyOutboxService:

    @staticmethod
    def enqueue(event_type: str, payload: dict) -> Optional[NotifyOutboxEvent]:
        """Persist an event for later delivery. Returns None (and logs)
        without raising if the DB write itself fails — a notification is
        never allowed to break the business operation that triggered it,
        the same guarantee the old synchronous BotNotifyService made."""
        try:
            event = NotifyOutboxEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
            )
            event.payload = payload
            db.session.add(event)
            db.session.commit()
            return event
        except Exception:
            logger.exception("Failed to enqueue outbox event %s", event_type)
            db.session.rollback()
            return None

    @staticmethod
    def _claim_batch(limit: int) -> list[NotifyOutboxEvent]:
        now = datetime.now(timezone.utc)
        candidates = (
            db.session.query(NotifyOutboxEvent)
            .filter(
                NotifyOutboxEvent.status == OutboxEventStatus.PENDING,
                NotifyOutboxEvent.next_attempt_at <= now,
            )
            .order_by(NotifyOutboxEvent.created_at)
            .limit(limit)
            .all()
        )
        claimed = []
        for event in candidates:
            # Conditional UPDATE — only takes effect if still PENDING, so a
            # second worker that also selected this row a moment ago loses
            # the race harmlessly (its update affects 0 rows).
            updated = (
                db.session.query(NotifyOutboxEvent)
                .filter(NotifyOutboxEvent.id == event.id, NotifyOutboxEvent.status == OutboxEventStatus.PENDING)
                .update({"status": OutboxEventStatus.PROCESSING}, synchronize_session=False)
            )
            db.session.commit()
            if updated:
                db.session.refresh(event)
                claimed.append(event)
        return claimed

    @staticmethod
    def _deliver(event: NotifyOutboxEvent) -> bool:
        base_url = current_app.config.get("BOT_EVENTS_URL")
        secret = current_app.config.get("INCOMING_EVENT_SECRET")
        if not base_url or not secret:
            logger.info(
                "NotifyOutboxService: BOT_EVENTS_URL/INCOMING_EVENT_SECRET не заданы — "
                "событие %s не отправлено (фича выключена).", event.event_type,
            )
            return False

        body = json.dumps(event.payload, ensure_ascii=False).encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

        try:
            import requests

            resp = requests.post(
                f"{base_url.rstrip('/')}/events/{event.event_type}",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature": signature,
                    "X-Event-Id": event.event_id,
                },
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if resp.status_code >= 400:
                event.last_error = f"HTTP {resp.status_code}"
                return False
            return True
        except Exception as e:
            event.last_error = f"{type(e).__name__}: {e}"[:2000]
            return False

    @staticmethod
    def drain(limit: int = 50) -> dict:
        """Claim up to `limit` due events and attempt delivery. Returns a
        small summary dict — used by both the `flask outbox-drain` CLI
        command and the optional in-process poller."""
        claimed = NotifyOutboxService._claim_batch(limit)
        delivered = failed = requeued = 0

        for event in claimed:
            ok = NotifyOutboxService._deliver(event)
            event.attempts += 1
            if ok:
                event.status = OutboxEventStatus.DELIVERED
                event.delivered_at = datetime.now(timezone.utc)
                delivered += 1
            elif event.attempts >= event.max_attempts:
                event.status = OutboxEventStatus.FAILED
                failed += 1
                logger.warning(
                    "Outbox event %s (%s) exhausted retries: %s",
                    event.event_id, event.event_type, event.last_error,
                )
            else:
                event.status = OutboxEventStatus.PENDING
                event.next_attempt_at = datetime.now(timezone.utc) + timedelta(
                    seconds=_backoff_seconds(event.attempts)
                )
                requeued += 1
            db.session.commit()

        return {
            "claimed": len(claimed), "delivered": delivered, "failed": failed, "requeued": requeued,
        }

    @staticmethod
    def requeue_failed(event_id: str) -> bool:
        """Manual re-send of a FAILED event (observability requirement:
        'безопасная ручная повторная отправка неудавшегося события')."""
        event = db.session.query(NotifyOutboxEvent).filter_by(event_id=event_id).first()
        if not event or event.status != OutboxEventStatus.FAILED:
            return False
        event.status = OutboxEventStatus.PENDING
        event.attempts = 0
        event.next_attempt_at = datetime.now(timezone.utc)
        event.last_error = None
        db.session.commit()
        return True
