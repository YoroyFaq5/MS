"""
NotifyOutboxService — durable delivery for site -> bot notifications,
implemented as a real transactional outbox.

Covers:
- enqueue() only stages a row in the CALLER's session (no commit/rollback
  of its own) — it commits/rolls back exactly when the caller's own
  transaction does, atomically together with whatever business change
  triggered it.
- enqueue_and_commit() is the deliberate standalone exception for call
  sites with no live surrounding transaction.
- drain() still delivers/retries/gives up correctly, and
  BotNotifyService.notify_player/notify_player_committed are drop-in
  wrappers around the two staging modes.
"""
from unittest.mock import patch

import pytest

from app import db
from app.models import (
    NotifyOutboxEvent, OutboxEventStatus, Achievement, AchievementCategory,
    AchievementTrigger, PlayerAchievement,
)
from app.services.notify_outbox_service import NotifyOutboxService
from app.services.bot_notify_service import BotNotifyService
from helpers import make_player


def _configure_bot_url(app):
    app.config["BOT_EVENTS_URL"] = "https://bot.example.test"
    app.config["INCOMING_EVENT_SECRET"] = "test-outbox-secret"


def _make_achievement(code: str = "test-ach") -> Achievement:
    ach = Achievement(
        code=code, name="Test Achievement",
        category=AchievementCategory.SOCIAL, trigger=AchievementTrigger.MANUAL,
    )
    db.session.add(ach)
    db.session.flush()
    return ach


# ── enqueue() basics ─────────────────────────────────────────────────────────

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


# ── Transactional-outbox atomicity ───────────────────────────────────────────

def test_business_operation_and_event_commit_together_in_one_commit(app_ctx):
    """The real AchievementService.unlock() call site: PlayerAchievement and
    its outbox event must both land with the SAME db.session.commit()."""
    from app.services.achievement_service import AchievementService

    player = make_player("Hero")
    player.telegram_id = "1001"
    ach = _make_achievement()
    db.session.commit()

    result = AchievementService.unlock(player.id, ach.code)
    assert result.ok

    assert db.session.query(PlayerAchievement).filter_by(player_id=player.id).count() == 1
    events = db.session.query(NotifyOutboxEvent).filter_by(event_type="achievement-granted").all()
    assert len(events) == 1
    assert events[0].payload["telegram_id"] == "1001"


def test_rollback_of_business_operation_also_rolls_back_event(app_ctx):
    """If the caller's transaction never commits (e.g. an error further
    down forces a rollback), the staged outbox event must vanish with it —
    proving enqueue() rode the SAME transaction, not one of its own."""
    player = make_player("Rollback Target")
    player.telegram_id = "2002"
    ach = _make_achievement("rollback-ach")
    db.session.commit()

    pa = PlayerAchievement(player_id=player.id, achievement_id=ach.id)
    db.session.add(pa)
    BotNotifyService.notify_player(
        player.id, "achievement-granted", {"achievement_name": ach.name},
    )
    # Simulate a failure elsewhere in the same request forcing a rollback
    # instead of the commit this business operation was heading towards.
    db.session.rollback()

    assert db.session.query(PlayerAchievement).filter_by(player_id=player.id).count() == 0
    assert db.session.query(NotifyOutboxEvent).count() == 0


def test_enqueue_does_not_commit_by_itself(app_ctx):
    """enqueue() must never call db.session.commit() — proven by staging an
    UNRELATED pending change first, calling enqueue(), then rolling back:
    if enqueue() had committed, the rollback below would have nothing left
    to undo and the unrelated row would still be visible afterwards."""
    player = make_player("Uncommitted")
    db.session.flush()  # player already has an id, but is NOT committed

    NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1"})
    db.session.rollback()

    from app.models import Player
    assert db.session.query(Player).filter_by(id=player.id).first() is None
    assert db.session.query(NotifyOutboxEvent).count() == 0


def test_enqueue_does_not_rollback_callers_pending_changes(app_ctx):
    """enqueue() must never call db.session.rollback() — proven by staging
    an unrelated pending change BEFORE enqueue(), then committing: if
    enqueue() had rolled back, the unrelated change would be gone even
    though we never rolled back ourselves."""
    player = make_player("Survives")
    player.telegram_id = "3003"
    db.session.commit()

    player.elo = 1234.5  # unrelated pending change, not yet committed
    NotifyOutboxService.enqueue("game-finished", {"telegram_id": "3003"})
    db.session.commit()

    db.session.refresh(player)
    assert player.elo == 1234.5
    assert db.session.query(NotifyOutboxEvent).count() == 1


def test_error_before_external_commit_leaves_no_event(app_ctx):
    """If the caller's business logic raises before it ever reaches its own
    db.session.commit(), the staged event must not exist — enqueue() must
    not have committed it behind the caller's back. The caller's own
    except-block rollback() (the realistic pattern) stands in for whatever
    cleanup a real failing service method would do."""
    def _business_operation_that_fails():
        NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1"})
        raise RuntimeError("business logic failed before its own commit")

    with pytest.raises(RuntimeError):
        try:
            _business_operation_that_fails()
        except RuntimeError:
            db.session.rollback()
            raise

    assert db.session.query(NotifyOutboxEvent).count() == 0


def test_enqueue_raises_on_bad_payload_instead_of_swallowing(app_ctx):
    """A payload that can't be JSON-serialized must raise, not be silently
    dropped — swallowing it here would let the caller's business change
    commit with no matching event, exactly the atomicity break the outbox
    exists to prevent."""
    class Unserializable:
        pass

    with pytest.raises(TypeError):
        NotifyOutboxService.enqueue("game-finished", {"bad": Unserializable()})


# ── enqueue_and_commit() — the explicit standalone exception ────────────────

def test_enqueue_and_commit_persists_immediately(app_ctx):
    event = NotifyOutboxService.enqueue_and_commit("next-slot", {"players": []})
    assert event is not None
    event_id = event.event_id
    db.session.remove()  # force a fresh session read — proves it's truly committed
    assert db.session.query(NotifyOutboxEvent).filter_by(event_id=event_id).count() == 1


def test_enqueue_and_commit_swallows_failure_and_returns_none(app_ctx):
    with patch("app.services.notify_outbox_service.NotifyOutboxService.enqueue", side_effect=RuntimeError("boom")):
        result = NotifyOutboxService.enqueue_and_commit("next-slot", {"players": []})
    assert result is None


def test_notify_player_committed_persists_immediately(app_ctx):
    player = make_player("Standalone")
    player.telegram_id = "4004"
    db.session.commit()

    ok = BotNotifyService.notify_player_committed(player.id, "game-finished", {"won": True})
    assert ok is True
    db.session.remove()
    events = db.session.query(NotifyOutboxEvent).filter_by(event_type="game-finished").all()
    assert len(events) == 1


def test_notify_player_committed_no_op_when_not_linked(app_ctx):
    player = make_player("StandaloneUnlinked")
    ok = BotNotifyService.notify_player_committed(player.id, "game-finished", {"won": True})
    assert ok is False
    assert db.session.query(NotifyOutboxEvent).count() == 0


# ── Delivery, retry, dedup continue to work ──────────────────────────────────

def test_drain_delivers_successful_event(app_ctx, app):
    _configure_bot_url(app)
    NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})
    db.session.commit()

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


def test_drain_sends_stable_event_id_header_for_bot_side_dedup(app_ctx, app):
    _configure_bot_url(app)
    event = NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})
    db.session.commit()

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        NotifyOutboxService.drain()

    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["X-Event-Id"] == event.event_id
    assert "X-Signature" in kwargs["headers"]


def test_drain_requeues_on_failure_with_backoff(app_ctx, app):
    _configure_bot_url(app)
    event = NotifyOutboxService.enqueue("game-finished", {"telegram_id": "1", "won": True})
    db.session.commit()

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
    db.session.commit()
    summary = NotifyOutboxService.drain()
    assert summary["claimed"] == 1
    assert summary["delivered"] == 0
