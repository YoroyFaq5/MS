"""
Миграция для привязки Telegram-аккаунта к игроку (Login Widget).

Запустить один раз на существующей базе:

    python migrate_player_telegram.py

Добавляет колонку players.telegram_id (nullable, unique) — она нужна,
чтобы Telegram-бот (отдельное приложение) мог резолвить "чей это
telegram_id" через API, не имея прямого доступа к базе данных.
Безопасно перезапускать: перед ALTER TABLE проверяется, существует ли
колонка уже.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'players' AND column_name = 'telegram_id'"
        )).scalar()

        if existing:
            print("Пропущено: players.telegram_id уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE players ADD COLUMN telegram_id VARCHAR(32) NULL UNIQUE;"
            ))
            conn.commit()
            print("OK: добавлена колонка players.telegram_id.")

print("Готово.")
