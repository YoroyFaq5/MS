"""
AuthService
===========
All authentication / authorization business logic.
No Flask request context used here — only SQLAlchemy + domain rules.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app import db
from app.models.user import User
from app.models import Player


# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
PASSWORD_MIN = 6


# ---------------------------------------------------------------------------
# Result type (no exceptions as control flow in views)
# ---------------------------------------------------------------------------

@dataclass
class AuthResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "AuthResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "AuthResult":
        return cls(ok=False, message=msg)


# ---------------------------------------------------------------------------
# AuthService
# ---------------------------------------------------------------------------

class AuthService:

    # ── Registration ─────────────────────────────────────────────────────────

    @staticmethod
    def register(
        username: str,
        password: str,
        email: str = "",
        player_id: Optional[int] = None,
        migration_mode: bool = False,
    ) -> AuthResult:
        """
        Create a new local User account.

        Args:
            username:  unique login name (3-32, alphanumeric + _)
            password:  plaintext — will be hashed
            email:     optional, stored if provided
            player_id: optional existing Player to link immediately
            migration_mode: пропускает проверку формата логина (regex —
                рассчитан на новые регистрации через форму, а не на
                исторические кириллические логины) и минимальной длины
                пароля (тоже современное требование, которого не было в
                старой системе). Уникальность логина/email — жёсткое
                ограничение БД, проверяется всегда, даже в этом режиме.
                Используется только Migration API (см. migration_service.py).
        """
        username = username.strip()
        email    = email.strip() or None

        # ── Validate username ──────────────────────────────────────────────
        if not migration_mode and not USERNAME_RE.match(username):
            return AuthResult.fail(
                "Логин: 3–32 символа, только буквы, цифры и '_'."
            )
        if not username:
            return AuthResult.fail("Логин обязателен.")

        if db.session.query(User).filter_by(username=username).first():
            return AuthResult.fail(f"Логин «{username}» уже занят.")

        # ── Validate email ─────────────────────────────────────────────────
        if email:
            if "@" not in email or "." not in email.split("@")[-1]:
                return AuthResult.fail("Некорректный e-mail.")
            if db.session.query(User).filter_by(email=email).first():
                return AuthResult.fail("Этот e-mail уже используется.")

        # ── Validate password ──────────────────────────────────────────────
        if not migration_mode and len(password) < PASSWORD_MIN:
            return AuthResult.fail(
                f"Пароль должен быть не менее {PASSWORD_MIN} символов."
            )

        # ── Validate player linkage ────────────────────────────────────────
        player = None
        if player_id:
            player = db.session.get(Player, player_id)
            if not player:
                return AuthResult.fail("Игрок не найден.")
            existing_link = db.session.query(User).filter_by(player_id=player_id).first()
            if existing_link:
                return AuthResult.fail(
                    f"Игрок «{player.display_name}» уже привязан к другому аккаунту."
                )

        # ── Create user ────────────────────────────────────────────────────
        user = User(
            username=username,
            email=email,
            auth_provider="local",
            player_id=player_id,
        )
        user.set_password(password)

        # First ever user becomes admin
        if db.session.query(User).count() == 0:
            user.is_admin = True

        db.session.add(user)
        db.session.commit()

        return AuthResult.success(
            f"Аккаунт «{username}» создан.", data=user
        )

    # ── Login ─────────────────────────────────────────────────────────────────

    @staticmethod
    def authenticate(username: str, password: str) -> AuthResult:
        """
        Verify credentials and return User on success.
        Updates last_login_at timestamp.
        """
        username = username.strip()
        user = db.session.query(User).filter_by(username=username).first()

        if not user:
            # Constant-time-ish: don't reveal whether username exists
            return AuthResult.fail("Неверный логин или пароль.")

        if not user.is_active:
            return AuthResult.fail("Аккаунт заблокирован. Обратитесь к администратору.")

        if not user.check_password(password):
            return AuthResult.fail("Неверный логин или пароль.")

        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()

        return AuthResult.success("Добро пожаловать!", data=user)

    # ── Password change ───────────────────────────────────────────────────────

    @staticmethod
    def change_password(
        user: User,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> AuthResult:
        if not user.check_password(current_password):
            return AuthResult.fail("Текущий пароль неверен.")
        if len(new_password) < PASSWORD_MIN:
            return AuthResult.fail(
                f"Новый пароль: минимум {PASSWORD_MIN} символов."
            )
        if new_password != confirm_password:
            return AuthResult.fail("Пароли не совпадают.")
        if new_password == current_password:
            return AuthResult.fail("Новый пароль совпадает со старым.")

        user.set_password(new_password)
        db.session.commit()
        return AuthResult.success("Пароль успешно изменён.")

    # ── Player linkage ────────────────────────────────────────────────────────

    @staticmethod
    def link_player(user: User, player_id: int) -> AuthResult:
        """
        Link an existing Player to a User account.
        Player statistics are preserved — only the FK is set.
        """
        if user.player_id:
            return AuthResult.fail(
                "Аккаунт уже привязан к игроку. Сначала отвяжите текущего."
            )

        player = db.session.get(Player, player_id)
        if not player:
            return AuthResult.fail("Игрок не найден.")
        if not player.is_active:
            return AuthResult.fail("Нельзя привязать неактивного игрока.")

        conflict = db.session.query(User).filter_by(player_id=player_id).first()
        if conflict:
            return AuthResult.fail(
                f"Игрок «{player.display_name}» уже привязан к аккаунту «{conflict.username}»."
            )

        user.player_id = player_id
        db.session.commit()
        return AuthResult.success(
            f"Игрок «{player.display_name}» успешно привязан.", data=player
        )

    @staticmethod
    def unlink_player(user: User) -> AuthResult:
        if not user.player_id:
            return AuthResult.fail("Нет привязанного игрока.")
        player_name = user.player.display_name if user.player else "?"
        user.player_id = None
        db.session.commit()
        return AuthResult.success(f"Игрок «{player_name}» отвязан.")

    # ── Telegram Login Widget ──────────────────────────────────────────────────
    # https://core.telegram.org/widgets/login — данные, полученные от виджета
    # (id, first_name, username, photo_url, auth_date, hash), подписаны
    # HMAC-SHA256 секретом SHA256(bot_token). Проверка обязательна — иначе
    # кто угодно может прислать произвольный telegram_id.

    MAX_AUTH_AGE_SECONDS = 86400  # сутки — защита от повторного использования старого ответа

    @staticmethod
    def verify_telegram_login_data(data: dict, bot_token: str) -> bool:
        import hashlib
        import hmac
        import time

        received_hash = data.get("hash")
        if not received_hash:
            return False

        auth_date = data.get("auth_date")
        if not auth_date or time.time() - int(auth_date) > AuthService.MAX_AUTH_AGE_SECONDS:
            return False

        fields = {k: v for k, v in data.items() if k != "hash"}
        data_check_string = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
        secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
        computed_hash = hmac.new(
            secret_key, data_check_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed_hash, received_hash)

    @staticmethod
    def link_telegram(player: Player, telegram_id: str) -> AuthResult:
        conflict = (
            db.session.query(Player)
            .filter(Player.telegram_id == telegram_id, Player.id != player.id)
            .first()
        )
        if conflict:
            return AuthResult.fail(
                f"Этот Telegram-аккаунт уже привязан к игроку «{conflict.display_name}»."
            )
        player.telegram_id = telegram_id
        db.session.commit()
        return AuthResult.success("Telegram успешно привязан.")

    @staticmethod
    def unlink_telegram(player: Player) -> AuthResult:
        if not player.telegram_id:
            return AuthResult.fail("Telegram не привязан.")
        player.telegram_id = None
        db.session.commit()
        return AuthResult.success("Telegram отвязан.")

    # ── Admin: user management ────────────────────────────────────────────────

    @staticmethod
    def set_admin(target_user: User, value: bool, actor: User) -> AuthResult:
        if not actor.is_admin:
            return AuthResult.fail("Недостаточно прав.")
        if target_user.id == actor.id and not value:
            return AuthResult.fail("Нельзя снять права администратора с самого себя.")
        target_user.is_admin = value
        db.session.commit()
        action = "получил" if value else "лишён"
        return AuthResult.success(
            f"Пользователь «{target_user.username}» {action} прав администратора."
        )

    @staticmethod
    def deactivate_user(target_user: User, actor: User) -> AuthResult:
        if not actor.is_admin:
            return AuthResult.fail("Недостаточно прав.")
        if target_user.id == actor.id:
            return AuthResult.fail("Нельзя заблокировать самого себя.")
        target_user.is_active = False
        db.session.commit()
        return AuthResult.success(
            f"Пользователь «{target_user.username}» заблокирован."
        )

    @staticmethod
    def activate_user(target_user: User, actor: User) -> AuthResult:
        if not actor.is_admin:
            return AuthResult.fail("Недостаточно прав.")
        target_user.is_active = True
        db.session.commit()
        return AuthResult.success(
            f"Пользователь «{target_user.username}» разблокирован."
        )

    @staticmethod
    def admin_change_username(target_user: User, new_username: str, actor: User) -> AuthResult:
        """Admin renames a login. Same format rules as self-registration."""
        if not actor.is_admin:
            return AuthResult.fail("Недостаточно прав.")
        new_username = new_username.strip()
        if not USERNAME_RE.match(new_username):
            return AuthResult.fail("Логин: 3–32 символа, только буквы, цифры и '_'.")
        if new_username == target_user.username:
            return AuthResult.fail("Это и есть текущий логин.")
        conflict = db.session.query(User).filter_by(username=new_username).first()
        if conflict:
            return AuthResult.fail(f"Логин «{new_username}» уже занят.")

        old_username = target_user.username
        target_user.username = new_username
        db.session.commit()
        return AuthResult.success(
            f"Логин изменён: «{old_username}» → «{new_username}»."
        )

    @staticmethod
    def admin_reset_password(target_user: User, new_password: str, actor: User) -> AuthResult:
        """
        Admin sets a new password directly — unlike change_password(), does
        NOT require knowing the current one (пароли хешированы, посмотреть
        существующий пароль невозможно в принципе — это и есть смысл
        хеширования; сброс на новый — единственный безопасный вариант
        "восстановить доступ" для админа).
        """
        if not actor.is_admin:
            return AuthResult.fail("Недостаточно прав.")
        if len(new_password) < PASSWORD_MIN:
            return AuthResult.fail(f"Пароль должен быть не менее {PASSWORD_MIN} символов.")

        target_user.set_password(new_password)
        db.session.commit()
        return AuthResult.success(
            f"Пароль пользователя «{target_user.username}» сброшен на новый."
        )

    # ── OAuth stub (future Telegram / Google) ─────────────────────────────────

    @staticmethod
    def get_or_create_oauth_user(
        provider: str,
        provider_id: str,
        username: str,
        email: Optional[str] = None,
    ) -> AuthResult:
        """
        Stub for OAuth providers (Telegram, Google, …).
        When implementing: call this after verifying the provider token.
        """
        user = db.session.query(User).filter_by(
            auth_provider=provider, provider_id=provider_id
        ).first()

        if user:
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()
            return AuthResult.success("OK", data=user)

        # Create new OAuth account (no password)
        base_username = username
        counter = 1
        while db.session.query(User).filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=email,
            auth_provider=provider,
            provider_id=provider_id,
            last_login_at=datetime.now(timezone.utc),
        )
        db.session.add(user)
        db.session.commit()
        return AuthResult.success("Аккаунт создан через OAuth.", data=user)
