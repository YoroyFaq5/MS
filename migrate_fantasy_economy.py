"""
Migration for the Fantasy Draft entry-fee/prize-pool rework.

Run once against an existing database (same pattern as check_db.py):

    python migrate_fantasy_economy.py

What it does:
1. Adds fantasy_drafts.entry_cost_paid (new column on an existing table —
   db.create_all() cannot add columns to tables that already exist).
2. Creates the economy_settings table if missing (a brand-new table would
   actually be picked up by `flask init-db` / db.create_all() too, but it's
   included here so a single script handles the whole upgrade).
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        for stmt in [
            "ALTER TABLE fantasy_drafts ADD COLUMN entry_cost_paid FLOAT NOT NULL DEFAULT 0;",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
                print(f"OK: {stmt}")
            except Exception as e:
                print(f"Skip: {e}")

    # New table — safe to create via the ORM metadata directly.
    from app.models import EconomySettings
    EconomySettings.__table__.create(bind=db.engine, checkfirst=True)
    print("OK: ensured economy_settings table exists")
