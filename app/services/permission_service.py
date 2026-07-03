"""
PermissionService
=================
Single source of truth for all access control decisions.

Rules:
- Admins can do everything.
- Regular users can only read + manage their own profile/fantasy.
- No permission checks in views or other services — always delegate here.

Usage:
    from app.services.permission_service import PermissionService, Permission

    # In a view:
    if not PermissionService.can(current_user, Permission.EDIT_GAME):
        abort(403)

    # Or via decorator (see auth_decorators.py):
    @requires_permission(Permission.CREATE_GAME)
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models import FantasyDraft, Game, Tournament, Season, Player


class Permission(Enum):
    # ── Games ────────────────────────────────────────────────────
    VIEW_GAME           = auto()
    CREATE_GAME         = auto()
    EDIT_GAME           = auto()
    DELETE_GAME         = auto()
    FINISH_GAME         = auto()

    # ── Tournaments ───────────────────────────────────────────────
    VIEW_TOURNAMENT     = auto()
    CREATE_TOURNAMENT   = auto()
    EDIT_TOURNAMENT     = auto()
    DELETE_TOURNAMENT   = auto()
    MANAGE_PARTICIPANTS = auto()
    MANAGE_STAGES       = auto()
    RUN_CUTOFF          = auto()

    # ── Players / Profiles ────────────────────────────────────────
    VIEW_PLAYER         = auto()
    EDIT_ANY_PLAYER     = auto()
    EDIT_OWN_PROFILE    = auto()

    # ── Seasons ───────────────────────────────────────────────────
    VIEW_SEASON         = auto()
    MANAGE_SEASONS      = auto()
    RESOLVE_TIEBREAK    = auto()
    CREATE_YEAR_TOURNAMENT = auto()

    # ── Ratings ───────────────────────────────────────────────────
    VIEW_RATINGS        = auto()

    # ── Economy ───────────────────────────────────────────────────
    VIEW_OWN_BALANCE    = auto()
    ADMIN_ADJUST_COINS  = auto()

    # ── Fantasy ───────────────────────────────────────────────────
    VIEW_FANTASY        = auto()
    CREATE_FANTASY_DRAFT = auto()
    EDIT_OWN_DRAFT      = auto()

    # ── Shop / Inventory ─────────────────────────────────────────
    VIEW_SHOP            = auto()
    PURCHASE_ITEM        = auto()
    EQUIP_ITEM           = auto()
    MANAGE_SHOP_ITEMS    = auto()   # admin: create/edit/deactivate/grant

    # ── Achievements ──────────────────────────────────────────────
    VIEW_ACHIEVEMENTS    = auto()
    PIN_ACHIEVEMENT      = auto()
    MANAGE_ACHIEVEMENTS  = auto()   # admin: create/edit + manual grant of SPECIAL

    # ── Titles / Nominations ─────────────────────────────────────
    VIEW_TITLES          = auto()
    EQUIP_TITLE          = auto()
    MANAGE_TITLES        = auto()   # admin: manual grant/revoke + rebuild nominations

    # ── Admin ─────────────────────────────────────────────────────
    MANAGE_USERS        = auto()
    VIEW_ADMIN_PANEL    = auto()


# ---------------------------------------------------------------------------
# Permission matrix
# ---------------------------------------------------------------------------

# Permissions available to ANY authenticated user
_USER_PERMISSIONS: frozenset[Permission] = frozenset({
    Permission.VIEW_GAME,
    Permission.VIEW_TOURNAMENT,
    Permission.VIEW_PLAYER,
    Permission.VIEW_SEASON,
    Permission.VIEW_RATINGS,
    Permission.VIEW_OWN_BALANCE,
    Permission.VIEW_FANTASY,
    Permission.CREATE_FANTASY_DRAFT,
    Permission.EDIT_OWN_PROFILE,
    Permission.EDIT_OWN_DRAFT,
    Permission.VIEW_SHOP,
    Permission.PURCHASE_ITEM,
    Permission.EQUIP_ITEM,
    Permission.VIEW_ACHIEVEMENTS,
    Permission.PIN_ACHIEVEMENT,
    Permission.VIEW_TITLES,
    Permission.EQUIP_TITLE,
})

# Additional permissions for admins (union with user permissions)
_ADMIN_EXTRA_PERMISSIONS: frozenset[Permission] = frozenset({
    Permission.CREATE_GAME,
    Permission.EDIT_GAME,
    Permission.DELETE_GAME,
    Permission.FINISH_GAME,
    Permission.CREATE_TOURNAMENT,
    Permission.EDIT_TOURNAMENT,
    Permission.DELETE_TOURNAMENT,
    Permission.MANAGE_PARTICIPANTS,
    Permission.MANAGE_STAGES,
    Permission.RUN_CUTOFF,
    Permission.EDIT_ANY_PLAYER,
    Permission.MANAGE_SEASONS,
    Permission.RESOLVE_TIEBREAK,
    Permission.CREATE_YEAR_TOURNAMENT,
    Permission.ADMIN_ADJUST_COINS,
    Permission.MANAGE_USERS,
    Permission.VIEW_ADMIN_PANEL,
    Permission.MANAGE_SHOP_ITEMS,
    Permission.MANAGE_ACHIEVEMENTS,
    Permission.MANAGE_TITLES,
})

_ADMIN_PERMISSIONS: frozenset[Permission] = _USER_PERMISSIONS | _ADMIN_EXTRA_PERMISSIONS


class PermissionService:

    @staticmethod
    def can(user: Optional["User"], permission: Permission) -> bool:
        """
        Primary check: does this user hold this permission?
        Unauthenticated users (None / anonymous) only have VIEW_* rights.
        """
        if user is None or not getattr(user, "is_authenticated", False):
            # Anonymous: read-only public views
            return permission in {
                Permission.VIEW_GAME,
                Permission.VIEW_TOURNAMENT,
                Permission.VIEW_PLAYER,
                Permission.VIEW_SEASON,
                Permission.VIEW_RATINGS,
                Permission.VIEW_FANTASY,
                Permission.VIEW_SHOP,
                Permission.VIEW_ACHIEVEMENTS,
                Permission.VIEW_TITLES,
            }

        if not user.is_active:
            return False

        if user.is_admin:
            return permission in _ADMIN_PERMISSIONS

        return permission in _USER_PERMISSIONS

    @staticmethod
    def require(user: Optional["User"], permission: Permission) -> None:
        """
        Raise PermissionDenied if the user lacks the permission.
        Call from service layer; views should use can() or the decorator.
        """
        if not PermissionService.can(user, permission):
            raise PermissionDenied(
                f"Permission denied: {permission.name} for user={getattr(user,'username','anonymous')}"
            )

    # ── Object-level checks ───────────────────────────────────────────────────

    @staticmethod
    def can_edit_draft(user: Optional["User"], draft: "FantasyDraft") -> bool:
        """User can only edit their own OPEN draft."""
        if user is None or not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        return draft.user_id == user.id and draft.status.value == "open"

    @staticmethod
    def can_edit_player(user: Optional["User"], player: "Player") -> bool:
        """User can edit their own linked player; admin can edit anyone."""
        if user is None or not user.is_authenticated:
            return False
        if user.is_admin:
            return True
        return getattr(user, "player_id", None) == player.id

    @staticmethod
    def can_finish_game(user: Optional["User"], game: "Game") -> bool:
        if not PermissionService.can(user, Permission.FINISH_GAME):
            return False
        return not game.is_finished

    # ── Batch check (for UI rendering) ───────────────────────────────────────

    @staticmethod
    def user_permissions(user: Optional["User"]) -> set[Permission]:
        """Return full set of permissions for template context."""
        if user is None or not getattr(user, "is_authenticated", False):
            return set()
        if user.is_admin:
            return set(_ADMIN_PERMISSIONS)
        return set(_USER_PERMISSIONS)

    @staticmethod
    def check(user: Optional["User"], permission: Permission) -> dict:
        """API-friendly response."""
        allowed = PermissionService.can(user, permission)
        return {
            "permission": permission.name,
            "allowed": allowed,
            "user": getattr(user, "username", None),
        }


class PermissionDenied(Exception):
    """Raised by PermissionService.require() when access is denied."""
    pass
