"""
NotifyOutboxService — durable delivery for site -> bot notifications.
Covers: enqueue never raises into the caller, drain() delivers/retries/
gives up correctly, and BotNotifyService.notify_player is a drop-in
replacement for the old synchronous version (same call signature, now
backed by the outbox).
"""
from unittest.mock import patch

from app import db
from app.models import NotifyOutboxEvent, OutboxEventStatus
from app.services.notify_outbox_service import NotifyOutboxService
from app.services.bot_notify_service import BotNotifyService
from helpers import make_player


def _configure_bot_url(app):
    app.config["BOT_EVENTS_URL"] = "https://bot.example.test"
    app.config["INCOMING_EVENT_SECRET"] = "test-outbox-secret"


def test_enqueue_persists_event_and_returns_it(app_ctx):
    event = NotifyOutboxService.enqueue("achievement-granted", {"telegram_id": "1", "achievement_name": "X"})
    assert event is not None
    assert event.status == OutboxEventStatus.PENDING
    row = db.session.get(NotifyOutboxEvent, event.id)
    assert row.event_type == "achievement-granted"
    assert row.payload["achievement_name"] == "X"


def test_notify_player_enqueues_when_linked(app_ctx):
    player = make_player("Notifiable")
    player.telegram_id = "777000111"
    db.session.commit()

    ok = BotNotifyService.notify_player(player.id, "title-granted", {"title_name": "Легенда"})
    assert ok is True
    events = db.session.query(NotifyOutboxEvent).filter_by(event_type="title-granted").all()
    assert len(events) == 1
    assert events[0].payload["telegram_id"] == "777000111"


def test_notify_player_no_op_when_not_linked(app_ctx):
    player = make_player("NotLinked")
    ok = BotNotifyService.notify_player(player.id, "title-granted", {"title_name": "X"})
    assert ok is False
    assert db.session.query(NotifyOutboxEvent).count() == 0


def test_drain_delivers_successful_event(app_ctx, app):
    _configure_bot_url(app)
    NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        summary = NotifyOutboxService.drain()

    assert summary == {"claimed": 1, "delivered": 1, "failed": 0, "requeued": 0}
    event = db.session.query(NotifyOutboxEvent).first()
    assert event.status == OutboxEventStatus.DELIVERED
    assert event.delivered_at is not None

    # Delivered events are never re-claimed by a later drain.
    with patch("requests.post") as mock_post:
        NotifyOutboxService.drain()
        mock_post.assert_not_called()


def test_drain_requeues_on_failure_with_backoff(app_ctx, app):
    _configure_bot_url(app)
    event = NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 500
        NotifyOutboxService.drain()

    db.session.refresh(event)
    assert event.status == OutboxEventStatus.PENDING
    assert event.attempts == 1
    assert event.next_attempt_at > event.created_at


def test_drain_marks_failed_after_max_attempts(app_ctx, app):
    _configure_bot_url(app)
    event = NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})
    event.max_attempts = 1
    db.session.commit()

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 500
        NotifyOutboxService.drain()

    db.session.refresh(event)
    assert event.status == OutboxEventStatus.FAILED


def test_requeue_failed_resets_for_another_attempt(app_ctx, app):
    _configure_bot_url(app)
    event = NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})
    event.status = OutboxEventStatus.FAILED
    event.attempts = 8
    db.session.commit()

    ok = NotifyOutboxService.requeue_failed(event.event_id)
    assert ok is True
    db.session.refresh(event)
    assert event.status == OutboxEventStatus.PENDING
    assert event.attempts == 0


def test_drain_without_bot_configured_does_not_crash(app_ctx, app):
    app.config["BOT_EVENTS_URL"] = None
    NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})
    summary = NotifyOutboxService.drain()
    assert summary["claimed"] == 1
    assert summary["delivered"] == 0
