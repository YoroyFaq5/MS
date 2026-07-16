"""
Миграция для бесплатного (тренировочного) режима фэнтези-драфта.

Запустить один раз на существующей базе:

    python migrate_fantasy_practice_mode.py

Добавляет колонку fantasy_drafts.is_practice (BOOL, NOT NULL, default 0) —
драфт без взноса и без права на приз (см. FantasyService — is_practice
исключается из призового банка/выплат, но остаётся в отдельном лидерборде).

Также пересоздаёт уникальный индекс (user_id, tournament_id,
tournament_series_id) с добавлением is_practice, чтобы один пользователь
мог иметь одновременно платный И тренировочный драфт на один турнир/серию.

Безопасно перезапускать: перед каждым изменением проверяется текущее
состояние схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column_exists = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'fantasy_drafts' AND column_name = 'is_practice'"
        )).scalar()

        if column_exists:
            print("Пропущено: fantasy_drafts.is_practice уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE fantasy_drafts "
                "ADD COLUMN is_practice TINYINT(1) NOT NULL DEFAULT 0;"
            ))
            conn.commit()
            print("OK: добавлена колонка fantasy_drafts.is_practice.")

        old_unique_exists = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.table_constraints "
            "WHERE table_schema = DATABASE() AND table_name = 'fantasy_drafts' "
            "AND constraint_name = 'uq_fantasy_user_tournament_series' "
            "AND constraint_type = 'UNIQUE'"
        )).scalar()
        # Проверяем, включает ли существующий индекс is_practice — если да,
        # значит уже пересоздан в прошлом запуске.
        already_has_is_practice = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() AND table_name = 'fantasy_drafts' "
            "AND index_name = 'uq_fantasy_user_tournament_series' "
            "AND column_name = 'is_practice'"
        )).scalar()

        if old_unique_exists and not already_has_is_practice:
            conn.execute(text(
                "ALTER TABLE fantasy_drafts "
                "DROP INDEX uq_fantasy_user_tournament_series;"
            ))
            conn.execute(text(
                "ALTER TABLE fantasy_drafts "
                "ADD UNIQUE KEY uq_fantasy_user_tournament_series "
                "(user_id, tournament_id, tournament_series_id, is_practice);"
            ))
            conn.commit()
            print("OK: пересоздан уникальный индекс с is_practice.")
        else:
            print("Пропущено: уникальный индекс уже включает is_practice (или не найден).")

print("Готово.")
