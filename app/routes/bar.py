"""
Bar Blueprint
=============
In-person coin redemptions at the club's bar — see app/services/
bar_service.py for the full anti-abuse design (signed short-lived QR
token, admin-only confirmation, immutable audit trail).

Flow: a logged-in player's own profile shows a QR (this blueprint's
qr_image, embedded there) encoding a signed link back into THIS blueprint;
an admin scans it, lands on redeem_confirm, and charges the player from
there. void_redemption is deliberately NOT nested under the token-scoped
URL — a mistake might be caught after the original QR has already expired,
and voiding is a pure admin_id + redemption_id operation with no need for
the customer's token to still be valid.
"""
import io

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response
from flask_login import current_user
import qrcode

from app import db
from app.models import Player, BarRedemption
from app.services import BarService
from app.auth_decorators import login_required, admin_required

bar_bp = Blueprint("bar", __name__)


@bar_bp.route("/qr.png")
@login_required
def qr_image():
    if not current_user.player_id:
        abort(404)

    token = BarService.build_redeem_token(current_user.player_id)
    redeem_url = url_for("bar.redeem_confirm", token=token, _external=True)

    img = qrcode.make(redeem_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    resp = Response(buf.getvalue(), mimetype="image/png")
    # Every request mints a fresh signed token — never let a browser/proxy
    # cache and hand out a stale one.
    resp.headers["Cache-Control"] = "no-store"
    return resp


@bar_bp.route("/redeem/<token>", methods=["GET", "POST"])
@admin_required
def redeem_confirm(token: str):
    player_id = BarService.verify_redeem_token(token)
    if player_id is None:
        flash("QR-код недействителен или истёк — попросите игрока показать код заново.", "danger")
        return redirect(url_for("bar.log"))

    player = db.session.get(Player, player_id)
    if not player:
        abort(404)

    if request.method == "POST":
        item_id = request.form.get("item_id", type=int)
        custom_amount = request.form.get("custom_amount", type=float)
        result = BarService.redeem(
            player_id=player.id,
            admin_id=current_user.id,
            item_id=item_id or None,
            custom_amount=custom_amount or None,
            note=request.form.get("note", ""),
        )
        flash(result.message, "success" if result.ok else "danger")
        return redirect(url_for("bar.redeem_confirm", token=token))

    catalog = BarService.list_catalog()
    recent = (
        db.session.query(BarRedemption)
        .filter_by(player_id=player.id)
        .order_by(BarRedemption.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template(
        "bar/redeem.html", player=player, catalog=catalog, recent=recent, token=token,
    )


@bar_bp.route("/void/<int:redemption_id>", methods=["POST"])
@admin_required
def void_redemption(redemption_id: int):
    result = BarService.void(redemption_id, current_user.id, request.form.get("reason", ""))
    flash(result.message, "success" if result.ok else "danger")
    return redirect(request.form.get("next") or url_for("bar.log"))


@bar_bp.route("/log")
@admin_required
def log():
    redemptions = BarService.recent(limit=200)
    return render_template("bar/log.html", redemptions=redemptions)
