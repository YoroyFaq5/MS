from flask import Blueprint, render_template, request

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
