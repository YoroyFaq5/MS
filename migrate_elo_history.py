"""
Migration for ELO history charting (Match history visualization).

Run once against an existing database (same pattern as migrate_fantasy_economy.py):

    python migrate_elo_history.py

What it does:
1. Adds game_slots.elo_after (new column on an existing table — db.create_all()
   cannot add columns to tables that already exist). Nullable, additive: games
   recorded before this migration simply have no ELO chart point for that game.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        for stmt in [
            "ALTER TABLE game_slots ADD COLUMN elo_after FLOAT;",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
                print(f"OK: {stmt}")
            except Exception as e:
                print(f"Skip: {e}")
