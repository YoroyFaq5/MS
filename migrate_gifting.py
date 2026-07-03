"""
Migration for the Marketplace / Gifting feature.

Run once against an existing database (same pattern as migrate_fantasy_economy.py):

    python migrate_gifting.py

What it does:
1. Adds shop_items.is_transferable and shop_items.giftable_message (new
   columns on an existing table — db.create_all() cannot add columns to
   tables that already exist). Both default to true (existing items stay
   giftable unless an admin turns it off).
2. Creates the gift_transfers table if missing (a brand-new table would
   actually be picked up by `flask init-db` / db.create_all() too, but it's
   included here so a single script handles the whole upgrade).
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        for stmt in [
            "ALTER TABLE shop_items ADD COLUMN is_transferable BOOLEAN NOT NULL DEFAULT 1;",
            "ALTER TABLE shop_items ADD COLUMN giftable_message BOOLEAN NOT NULL DEFAULT 1;",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
                print(f"OK: {stmt}")
            except Exception as e:
                print(f"Skip: {e}")

    # New table — safe to create via the ORM metadata directly.
    from app.models import GiftTransfer
    GiftTransfer.__table__.create(bind=db.engine, checkfirst=True)
    print("OK: ensured gift_transfers table exists")
