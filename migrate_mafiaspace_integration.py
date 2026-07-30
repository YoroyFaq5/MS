"""
Миграция для интеграции с MafiaSpace (внешние вебхуки с готовыми играми).

Запустить один раз на существующей базе:

    python migrate_mafiaspace_integration.py

Создаёт таблицы external_player_links и external_game_imports (см.
app/models/external_import.py). Обе — новые таблицы, поэтому (как и в
migrate_gifting.py) безопасно создаются напрямую через ORM-метаданные
модели, а не руками написанным ALTER/CREATE TABLE — так колонки/индексы
гарантированно совпадают с определением модели.

Безопасно перезапускать: checkfirst=True не трогает уже существующие таблицы.
"""
from app import create_app, db
from app.models import ExternalPlayerLink, ExternalGameImport

app = create_app("development")

with app.app_context():
    ExternalPlayerLink.__table__.create(bind=db.engine, checkfirst=True)
    print("OK: ensured external_player_links table exists")
    ExternalGameImport.__table__.create(bind=db.engine, checkfirst=True)
    print("OK: ensured external_game_imports table exists")

print("Готово.")
