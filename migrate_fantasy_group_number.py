"""
Миграция для групп эксклюзивного фэнтези-драфта на серию.

Запустить один раз на существующей базе:

    python migrate_fantasy_group_number.py

Добавляет колонку fantasy_drafts.group_number (INT, nullable) — группа
эксклюзивности внутри серии (см. FantasyService._assign_group). NULL —
обычный turnирный-wide драфт или ещё не сгруппированная запись,
поведение как раньше.

Безопасно перезапускать: перед ALTER TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column_exists = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'fantasy_drafts' AND column_name = 'group_number'"
        )).scalar()

        if column_exists:
            print("Пропущено: fantasy_drafts.group_number уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE fantasy_drafts "
                "ADD COLUMN group_number INT NULL;"
            ))
            conn.commit()
            print("OK: добавлена колонка fantasy_drafts.group_number.")

print("Готово.")
