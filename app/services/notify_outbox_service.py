"""
NotifyOutboxService
====================
Durable delivery for site -> MS-TG notifications, implemented as a real
transactional outbox:

- enqueue() only stages a NotifyOutboxEvent in the CALLER's own db.session
  — it never calls commit() or rollback(). The event rides the exact same
  commit as whatever business operation triggered it (a purchase, a gift,
  an achievement unlock, ...): call it BEFORE that operation's own
  db.session.commit(). If that transaction rolls back, the staged event
  vanishes with it, exactly like any other pending row; if it commits, the
  business change and the event become durable together, atomically.
- enqueue_and_commit() is the deliberate exception: a handful of call
  sites (see BotNotifyService.notify_player_committed /
  send_event_committed) fire *after* their triggering business operation
  already committed — e.g. a route handler notifying about a service call
  whose own transaction already finished earlier in the same request.
  There is no live transaction left to ride there, so this opens and
  commits its own short transaction instead, and never raises into the
  caller (a notification must not break a request whose business data is
  already safely committed). Use it only for genuinely detached,
  best-effort notifications — anywhere a business change and its
  notification must share fate, use enqueue() inside that operation's own
  transactional boundary instead.

What the outbox (either path) still fixes relative to the old fully-
synchronous BotNotifyService: the bot being down/slow no longer blocks or
risks the request that triggered the notification — delivery is a
separate step (drain()); a delivery failure is retried with exponential
backoff instead of being silently dropped after one attempt; every attempt
is visible (status/attempts/last_error) instead of only a log line, and a
stuck FAILED event can be manually re-queued.

drain() is a standalone process/worker path (the `flask outbox-drain` CLI
command or the optional in-process poller) — never nested inside a
business request — so it manages its own commits per claimed batch/event;
that's unrelated to the atomicity guarantee above. It's also safe to run
from multiple processes/threads at once: each event is claimed via an
atomic conditional UPDATE (only succeeds if the row is still PENDING), so
two workers racing on the same row never both send it.
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
    def enqueue(event_type: str, payload: dict) -> NotifyOutboxEvent:
        """Stage an outbox event in the CALLER's current transaction —
        deliberately no commit/rollback here (see module docstring): the
        caller's own eventual db.session.commit() is what makes this event
        durable, atomically together with whatever business row(s) it just
        changed. Call this BEFORE that commit.

        Issues a flush (not a commit) so the row gets its primary key and
        is visible to any query run later in the same transaction — a
        flush is fully undone by a rollback like any other pending change,
        so this does not weaken atomicity.

        Raises on genuine failure (e.g. a non-JSON-serializable payload) —
        deliberately not swallowed: silently returning here while the
        caller goes on to commit its business change would leave that
        change committed with no matching event, exactly the atomicity
        break this pattern exists to prevent. Let it propagate so the
        caller's own transaction fails/rolls back as a whole."""
        event = NotifyOutboxEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
        )
        event.payload = payload
        db.session.add(event)
        db.session.flush()
        return event

    @staticmethod
    def enqueue_and_commit(event_type: str, payload: dict) -> Optional[NotifyOutboxEvent]:
        """Standalone variant for the few call sites that fire *after*
        their triggering business transaction already committed (see
        module docstring) — opens and commits its own short transaction.
        Never raises into the caller: a notification is not allowed to
        break a request whose business data is already safely committed."""
        try:
            event = NotifyOutboxService.enqueue(event_type, payload)
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
