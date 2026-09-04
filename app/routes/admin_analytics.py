from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.services import AdminAnalyticsService, GiftService
from app.auth_decorators import admin_required

admin_analytics_bp = Blueprint("admin_analytics", __name__)


@admin_analytics_bp.route("/social")
@admin_required
def social():
    rivalries = AdminAnalyticsService.get_top_rivalries()
    most_gifted = AdminAnalyticsService.get_most_gifted_items()
    return render_template("admin_analytics/social.html", rivalries=rivalries, most_gifted=most_gifted)


@admin_analytics_bp.route("/gifts")
@admin_required
def gifts():
    page = request.args.get("page", 1, type=int)
    per_page = 50
    transfers = GiftService.get_all_transfers(limit=per_page, offset=(page - 1) * per_page)
    return render_template("admin_analytics/gifts.html", transfers=transfers, page=page)


@admin_analytics_bp.route("/outbox")
@admin_required
def outbox():
    """Observability for site -> Telegram-bot notifications — see
    app/services/notify_outbox_service.py. Shows the most recent events of
    each status so an admin can see whether delivery is healthy and
    manually re-queue a FAILED one."""
    from app.models import NotifyOutboxEvent

    status_filter = request.args.get("status")
    query = db.session.query(NotifyOutboxEvent).order_by(NotifyOutboxEvent.created_at.desc())
    if status_filter:
        query = query.filter(NotifyOutboxEvent.status == status_filter)
    events = query.limit(100).all()

    counts = {
        row[0].value: row[1]
        for row in db.session.query(NotifyOutboxEvent.status, db.func.count(NotifyOutboxEvent.id))
        .group_by(NotifyOutboxEvent.status).all()
    }
    return render_template(
        "admin_analytics/outbox.html", events=events, counts=counts, status_filter=status_filter,
    )


@admin_analytics_bp.route("/outbox/<event_id>/requeue", methods=["POST"])
@admin_required
def outbox_requeue(event_id: str):
    from app.services.notify_outbox_service import NotifyOutboxService

    ok = NotifyOutboxService.requeue_failed(event_id)
    flash(
        "Событие поставлено на повторную отправку." if ok else "Событие не найдено или не в статусе failed.",
        "success" if ok else "danger",
    )
    return redirect(url_for("admin_analytics.outbox"))
