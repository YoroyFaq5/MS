"""
Миграция: история изменений внешних импортов (external_game_import_revisions).

Запустить один раз на существующей базе (после migrate_mafiaspace_integration.py):

    python migrate_mafiaspace_revisions.py

Новая таблица — как и в migrate_gifting.py/migrate_mafiaspace_integration.py,
создаётся напрямую через ORM-метаданные модели (checkfirst=True), а не
руками написанным CREATE TABLE.
"""
from app import create_app, db
from app.models import ExternalGameImportRevision

app = create_app("development")

with app.app_context():
    ExternalGameImportRevision.__table__.create(bind=db.engine, checkfirst=True)
    print("OK: ensured external_game_import_revisions table exists")

print("Готово.")
