"""
Auth Blueprint
==============
HTTP layer only. All logic delegated to AuthService.
Routes: /auth/register, /auth/login, /auth/logout,
        /auth/profile, /auth/password,
        /auth/profile/link-player, /auth/profile/unlink-player
        /auth/admin/users  (admin panel)
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, jsonify
)
from flask_login import login_user, logout_user, current_user

from app import db
from app.models.user import User
from app.models import Player
from app.services.auth_service import AuthService
from app.auth_decorators import login_required, admin_required, anonymous_required

auth_bp = Blueprint("auth", __name__)


# ── Register ──────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_required
def register():
    # Collect unlinked players for the optional link dropdown
    linked_player_ids = {
        u.player_id
        for u in db.session.query(User).filter(User.player_id.isnot(None)).all()
    }
    free_players = (
        db.session.query(Player)
        .filter(Player.is_active == True, ~Player.id.in_(linked_player_ids))
        .order_by(Player.name)
        .all()
    )

    if request.method == "POST":
        result = AuthService.register(
            username=request.form.get("username", ""),
            password=request.form.get("password", ""),
            email=request.form.get("email", ""),
            player_id=request.form.get("player_id", type=int) or None,
        )
        if result.ok:
            login_user(result.data, remember=False)
            flash(result.message, "success")
            return redirect(url_for("main.index"))
        flash(result.message, "danger")

    return render_template("auth/register.html", free_players=free_players)


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
@anonymous_required
def login():
    if request.method == "POST":
        result = AuthService.authenticate(
            username=request.form.get("username", ""),
            password=request.form.get("password", ""),
        )
        if result.ok:
            remember = bool(request.form.get("remember"))
            login_user(result.data, remember=remember)
            flash(result.message, "success")
            next_page = request.args.get("next") or url_for("main.index")
            # Security: only allow same-site relative redirects (block
            # absolute URLs like "http://evil.com" and protocol-relative
            # URLs like "//evil.com" which browsers treat as absolute).
            if not next_page.startswith("/") or next_page.startswith("//"):
                next_page = url_for("main.index")
            return redirect(next_page)
        flash(result.message, "danger")

    return render_template("auth/login.html")


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))


# ── Profile ───────────────────────────────────────────────────────────────────
# Retired — superseded by the new /profile page (app/routes/profile.py).
# Kept as a redirect shim so old links/bookmarks keep working. Account
# linking (below) stays here — it's a User<->Player identity concern, not
# a profile-display concern.

@auth_bp.route("/profile")
@login_required
def profile():
    return redirect(url_for("profile.own_profile"))


# ── Change password ───────────────────────────────────────────────────────────

@auth_bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        result = AuthService.change_password(
            user=current_user,
            current_password=request.form.get("current_password", ""),
            new_password=request.form.get("new_password", ""),
            confirm_password=request.form.get("confirm_password", ""),
        )
        flash(result.message, "success" if result.ok else "danger")
        if result.ok:
            return redirect(url_for("profile.own_profile") if current_user.player_id else url_for("main.index"))

    return render_template("auth/password.html")


# ── Player linkage ────────────────────────────────────────────────────────────
# The new /profile page requires a linked Player to resolve, so account
# linking still needs its own small page — this is a User<->Player identity
# concern, kept in auth_bp per the plan (not a profile-display concern).

@auth_bp.route("/link-player")
@login_required
def link_player_page():
    if current_user.player_id:
        return redirect(url_for("profile.own_profile"))

    linked_ids = {
        u.player_id
        for u in db.session.query(User).filter(User.player_id.isnot(None)).all()
    }
    free_players = (
        db.session.query(Player)
        .filter(Player.is_active == True, ~Player.id.in_(linked_ids))
        .order_by(Player.name)
        .all()
    )
    return render_template("auth/link_player.html", free_players=free_players)


@auth_bp.route("/profile/link-player", methods=["POST"])
@login_required
def link_player():
    player_id = request.form.get("player_id", type=int)
    if not player_id:
        flash("Выберите игрока.", "danger")
        return redirect(url_for("auth.link_player_page"))
    result = AuthService.link_player(current_user, player_id)
    flash(result.message, "success" if result.ok else "danger")
    if result.ok:
        try:
            from app.services import AchievementService
            AchievementService.unlock(player_id, "account_linked")
        except Exception:
            pass
        return redirect(url_for("profile.view_profile", player_id=player_id))
    return redirect(url_for("auth.link_player_page"))


@auth_bp.route("/profile/unlink-player", methods=["POST"])
@login_required
def unlink_player():
    result = AuthService.unlink_player(current_user)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.link_player_page"))


# ── Telegram Login Widget (привязка к Telegram-боту) ───────────────────────────
# Виджет (data-auth-url) редиректит браузер сюда же с query-параметрами —
# это обычная навигация в том же браузере, сессионная кука Flask-Login при
# этом сохраняется, поэтому @login_required работает как обычно.

@auth_bp.route("/telegram/callback")
@login_required
def telegram_callback():
    from flask import current_app

    if not current_user.player_id:
        flash("Сначала привяжите аккаунт к игроку.", "warning")
        return redirect(url_for("auth.link_player_page"))

    bot_token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        flash("Привязка Telegram сейчас недоступна на сервере.", "danger")
        return redirect(url_for("profile.view_profile", player_id=current_user.player_id))

    data = request.args.to_dict()
    if not AuthService.verify_telegram_login_data(data, bot_token):
        flash("Не удалось проверить данные от Telegram — попробуйте ещё раз.", "danger")
        return redirect(url_for("profile.view_profile", player_id=current_user.player_id))

    result = AuthService.link_telegram(current_user.player, data["id"])
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.view_profile", player_id=current_user.player_id))


@auth_bp.route("/telegram/unlink", methods=["POST"])
@login_required
def telegram_unlink():
    if not current_user.player_id:
        abort(404)
    result = AuthService.unlink_telegram(current_user.player)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.view_profile", player_id=current_user.player_id))


# ── Admin: user list ──────────────────────────────────────────────────────────

@auth_bp.route("/admin/users")
@admin_required
def admin_users():
    users = db.session.query(User).order_by(User.created_at.desc()).all()
    return render_template("auth/admin_users.html", users=users)


@auth_bp.route("/admin/users/<int:user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_admin(user_id: int):
    target = db.session.get(User, user_id) or abort(404)
    new_val = not target.is_admin
    result = AuthService.set_admin(target, new_val, current_user)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_users"))


@auth_bp.route("/admin/users/<int:user_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_active(user_id: int):
    target = db.session.get(User, user_id) or abort(404)
    if target.is_active:
        result = AuthService.deactivate_user(target, current_user)
    else:
        result = AuthService.activate_user(target, current_user)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_users"))


@auth_bp.route("/admin/users/<int:user_id>/edit")
@admin_required
def admin_user_edit(user_id: int):
    target = db.session.get(User, user_id) or abort(404)
    return render_template("auth/admin_user_edit.html", target=target)


@auth_bp.route("/admin/users/<int:user_id>/change-username", methods=["POST"])
@admin_required
def admin_change_username(user_id: int):
    target = db.session.get(User, user_id) or abort(404)
    result = AuthService.admin_change_username(
        target, request.form.get("username", ""), current_user
    )
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_user_edit", user_id=user_id))


@auth_bp.route("/admin/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def admin_reset_password(user_id: int):
    target = db.session.get(User, user_id) or abort(404)
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    if new_password != confirm_password:
        flash("Пароли не совпадают.", "danger")
        return redirect(url_for("auth.admin_user_edit", user_id=user_id))
    result = AuthService.admin_reset_password(target, new_password, current_user)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_user_edit", user_id=user_id))


# ── API ───────────────────────────────────────────────────────────────────────

@auth_bp.route("/api/me")
@login_required
def api_me():
    return jsonify(current_user.to_dict())


# ── Admin: economy panel ──────────────────────────────────────────────────────

@auth_bp.route("/admin/economy")
@admin_required
def admin_economy():
    from app.models import Player, CoinTransaction
    from app.services.economy_service import EconomyService

    players = (
        db.session.query(Player)
        .filter_by(is_active=True)
        .order_by(Player.name)
        .all()
    )
    # Recent transactions across all players
    recent_txs = (
        db.session.query(CoinTransaction)
        .order_by(CoinTransaction.created_at.desc())
        .limit(30)
        .all()
    )
    settings = EconomyService.get_settings()
    return render_template(
        "auth/admin_economy.html",
        players=players,
        recent_txs=recent_txs,
        settings=settings,
    )


@auth_bp.route("/admin/economy/adjust", methods=["POST"])
@admin_required
def admin_economy_adjust():
    from app.models import Player
    from app.services.economy_service import EconomyService

    player_id = request.form.get("player_id", type=int)
    amount    = request.form.get("amount", type=float)
    reason    = request.form.get("reason", "").strip()

    if not player_id or amount is None:
        flash("Укажите игрока и сумму.", "danger")
        return redirect(url_for("auth.admin_economy"))

    player = db.session.get(Player, player_id)
    if not player:
        flash("Игрок не найден.", "danger")
        return redirect(url_for("auth.admin_economy"))

    result = EconomyService.admin_adjust(player, amount, reason)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_economy"))


@auth_bp.route("/admin/economy/bulk-adjust", methods=["POST"])
@admin_required
def admin_economy_bulk_adjust():
    from app.models import Player
    from app.services.economy_service import EconomyService

    player_ids = request.form.getlist("player_ids", type=int)
    amount     = request.form.get("amount", type=float)
    reason     = request.form.get("reason", "").strip()

    if not player_ids:
        flash("Выберите хотя бы одного игрока.", "danger")
        return redirect(url_for("auth.admin_economy"))
    if amount is None:
        flash("Укажите сумму.", "danger")
        return redirect(url_for("auth.admin_economy"))

    players = db.session.query(Player).filter(Player.id.in_(player_ids)).all()
    result = EconomyService.admin_bulk_adjust(players, amount, reason)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_economy"))


@auth_bp.route("/admin/economy/reset-all", methods=["POST"])
@admin_required
def admin_economy_reset_all():
    from app.services.economy_service import EconomyService

    confirm = request.form.get("confirm_reset", "")
    if confirm != "СБРОСИТЬ":
        flash("Сброс не выполнен — подтверждение не совпало.", "danger")
        return redirect(url_for("auth.admin_economy"))

    result = EconomyService.reset_all_balances()
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_economy"))


@auth_bp.route("/admin/economy/fantasy-settings", methods=["POST"])
@admin_required
def admin_economy_fantasy_settings():
    from app.services.economy_service import EconomyService

    entry_cost  = request.form.get("fantasy_entry_cost", type=float)
    first_share = request.form.get("fantasy_first_place_share", type=float)
    second_share = request.form.get("fantasy_second_place_share", type=float)

    # Form sends shares as whole percent (e.g. 70), convert to 0..1
    if first_share is not None:
        first_share = first_share / 100
    if second_share is not None:
        second_share = second_share / 100

    result = EconomyService.update_settings(
        fantasy_entry_cost=entry_cost,
        fantasy_first_place_share=first_share,
        fantasy_second_place_share=second_share,
    )
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("auth.admin_economy"))
