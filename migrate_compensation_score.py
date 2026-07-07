"""
Миграция для компенсационных баллов (Правила ФСМ, п.8.6.1-8.6.5).

Запустить один раз на существующей базе:

    python migrate_compensation_score.py

Добавляет колонку game_slots.compensation_score (FLOAT, default 0.0,
NOT NULL) — компенсация игроку, убитому в 1-ю ночь на роли мирного/шерифа,
пересчитываемая RatingService.recompute_compensation_points() на
дистанции турнира целиком. Безопасно перезапускать.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column_exists = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'game_slots' AND column_name = 'compensation_score'"
        )).scalar()

        if column_exists:
            print("Пропущено: game_slots.compensation_score уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE game_slots "
                "ADD COLUMN compensation_score FLOAT NOT NULL DEFAULT 0.0;"
            ))
            conn.commit()
            print("OK: добавлена колонка game_slots.compensation_score.")

print("Готово.")
