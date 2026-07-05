"""
Миграция для авторассадки турниров.

Запустить один раз на существующей базе:

    python migrate_game_round_number.py

Добавляет колонку games.round_number (nullable) — группирует игры,
сыгранные "параллельно" за разными столами одного раунда стадии турнира.
NULL — для обычных ручных/не турнирных игр без концепции раундов.
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
            "AND table_name = 'games' AND column_name = 'round_number'"
        )).scalar()

        if existing:
            print("Пропущено: games.round_number уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE games ADD COLUMN round_number INT NULL;"
            ))
            conn.commit()
            print("OK: добавлена колонка games.round_number.")

print("Готово.")
