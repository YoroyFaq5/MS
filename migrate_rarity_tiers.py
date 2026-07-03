"""
Migration for the Mythic/Ultra rarity tiers (unique, buyout-able shop items).

Run once against an existing database:

    python migrate_rarity_tiers.py

What it does:
1. Widens the MySQL ENUM definition of `rarity` on all three tables that
   share the Rarity Python enum (shop_items, achievements, titles) to
   include the two new values 'mythic' and 'ultra'. db.create_all() only
   creates missing tables — it cannot widen a native ENUM column on a
   table that already exists, so this has to run as ALTER TABLE.
   Safe to re-run: MODIFY COLUMN with the same target definition is a
   no-op, not an error.
2. Does NOT touch any existing row's rarity value — nothing currently in
   the database becomes mythic/ultra automatically. Run `flask
   update-shop-prices` (or re-seed) afterwards to actually create/update
   the new mythic/ultra items themselves.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

RARITY_VALUES = "'common','rare','epic','legendary','mythic','ultra'"

with app.app_context():
    with db.engine.connect() as conn:
        for stmt in [
            f"ALTER TABLE shop_items MODIFY COLUMN rarity ENUM({RARITY_VALUES}) NOT NULL;",
            f"ALTER TABLE achievements MODIFY COLUMN rarity ENUM({RARITY_VALUES}) NOT NULL;",
            f"ALTER TABLE titles MODIFY COLUMN rarity ENUM({RARITY_VALUES}) NOT NULL;",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
                print(f"OK: {stmt}")
            except Exception as e:
                print(f"Skip: {e}")

print("Готово.")
