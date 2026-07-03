from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    db.session.execute(text("""
        UPDATE players
        SET nickname = name
        WHERE nickname IS NULL OR nickname = ''
    """))
    db.session.commit()