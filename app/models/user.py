"""
User model
==========
Kept in a separate file to make the auth domain explicit.
Imported into models/__init__.py so SQLAlchemy sees it.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app import db


class User(UserMixin, db.Model):
    """
    Authentication identity. Decoupled from Player:
      - A Player can exist without a User (club member without account).
      - A User can exist without a Player (admin account).
      - One Player ↔ one User via Player.user_id (nullable FK).

    OAuth readiness:
      - auth_provider: 'local' | 'telegram' | 'google' …
      - provider_id:   provider-specific user ID (None for local)
    """
    __tablename__ = "users"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)

    # ── Identity ──────────────────────────────────────────────────────────
    username = Column(String(64), unique=True, nullable=False, index=True)
    email    = Column(String(120), unique=True, nullable=True, index=True)

    # ── Auth ──────────────────────────────────────────────────────────────
    password_hash   = Column(String(256), nullable=True)   # None for OAuth-only accounts
    auth_provider   = Column(String(32),  nullable=False, default="local")
    provider_id     = Column(String(128), nullable=True)   # OAuth provider user ID

    # ── Roles ─────────────────────────────────────────────────────────────
    is_admin        = Column(Boolean, default=False, nullable=False)
    is_active       = Column(Boolean, default=True,  nullable=False)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # ── Player linkage (one-to-one, nullable) ──────────────────────────────
    # The FK lives on User so a Player can be unlinked without cascade issues.
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,   # one User per Player
    )
    player = relationship(
        "Player",
        foreign_keys=[player_id],
        backref=db.backref("user", uselist=False),
    )

    # ── Password helpers ──────────────────────────────────────────────────

    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw)

    # ── Flask-Login interface ─────────────────────────────────────────────

    def get_id(self) -> str:
        return str(self.id)

    @property
    def is_player(self) -> bool:
        """True when this user is linked to a Player record."""
        return self.player_id is not None

    @property
    def display_name(self) -> str:
        if self.player:
            return self.player.display_name
        return self.username

    def __repr__(self) -> str:
        return f"<User {self.username!r} admin={self.is_admin}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "auth_provider": self.auth_provider,
            "player_id": self.player_id,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
