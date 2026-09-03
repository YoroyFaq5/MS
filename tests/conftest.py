"""
Pytest fixtures for the MafiaTracker test suite.

Uses a file-backed SQLite database (not `sqlite://` in-memory) so the
schema and data survive across the multiple connections Flask-SQLAlchemy
opens over the course of a test — avoids the "each connection gets its own
empty in-memory DB" trap. The DB file lives in a session-scoped temp
directory and is torn down automatically by pytest's `tmp_path_factory`.

DATABASE_URL must be set before `app.config` is first imported (it raises
RuntimeError otherwise, by design — see app/config.py), so this happens at
module import time, before any `from app...` import below.
"""
import os
import tempfile

_tmp_dir = tempfile.mkdtemp(prefix="mafiatracker_test_")
_db_path = os.path.join(_tmp_dir, "test.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_db_path}")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest

from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    application = create_app("development")
    application.config["SERVER_NAME"] = "testserver.local"
    application.config["WTF_CSRF_ENABLED"] = False
    yield application


@pytest.fixture()
def app_ctx(app):
    """Fresh schema per test — simplest reliable isolation for a small
    suite (drop/create beats hand-rolled savepoint bookkeeping across the
    many services under test, each committing independently)."""
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db(app_ctx):
    return _db


@pytest.fixture()
def client(app_ctx):
    return app_ctx.test_client()


def login_as(client, user):
    """Log a User in for a test client session without going through the
    real /auth/login form (see flask_login's own testing docs for this
    pattern: it only cares about session['_user_id'])."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True
