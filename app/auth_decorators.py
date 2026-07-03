"""
Auth decorators
===============
Thin wrappers around Flask-Login for route protection.
Import and use in any blueprint.
"""
from functools import wraps

from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def login_required(f):
    """Redirect to login page if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Войдите в аккаунт для доступа к этой странице.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Return 403 if user is not admin. Implies login_required."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Войдите в аккаунт для доступа к этой странице.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def anonymous_required(f):
    """Redirect authenticated users away (e.g. from /login when already logged in)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


def requires_permission(permission):
    """
    Route decorator that checks PermissionService.can().
    Usage:
        @requires_permission(Permission.CREATE_GAME)
        def new_game(): ...
    """
    from functools import wraps
    from flask import abort
    from flask_login import current_user
    from app.services.permission_service import PermissionService

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                from flask import flash, redirect, url_for, request
                flash("Войдите в аккаунт для доступа к этой странице.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            if not PermissionService.can(current_user, permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator
