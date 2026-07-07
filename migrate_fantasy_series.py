"""
Миграция для Fantasy-драфтов на отдельную серию турнира.

Запустить один раз на существующей базе:

    python migrate_fantasy_series.py

Добавляет колонку fantasy_drafts.tournament_series_id (nullable FK на
tournament_series.id) — позволяет драфту быть привязанным к одной серии
(игровому вечеру) внутри серийного турнира вместо всего турнира целиком.
NULL — обычный турнирный-wide драфт, поведение как было всегда.

Также заменяет UNIQUE("user_id", "tournament_id") на
UNIQUE("user_id", "tournament_id", "tournament_series_id") — старое
ограничение не давало создать серийный-скоуп драфт, если у пользователя
уже был обычный драфт на весь турнир (или наоборот).

Безопасно перезапускать: перед каждым ALTER TABLE проверяется текущее
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
            "AND table_name = 'fantasy_drafts' AND column_name = 'tournament_series_id'"
        )).scalar()

        if column_exists:
            print("Пропущено: fantasy_drafts.tournament_series_id уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE fantasy_drafts "
                "ADD COLUMN tournament_series_id INT NULL, "
                "ADD CONSTRAINT fk_fantasy_drafts_tournament_series "
                "FOREIGN KEY (tournament_series_id) REFERENCES tournament_series(id) "
                "ON DELETE CASCADE;"
            ))
            conn.commit()
            print("OK: добавлена колонка fantasy_drafts.tournament_series_id.")

        old_constraint = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.table_constraints "
            "WHERE table_schema = DATABASE() AND table_name = 'fantasy_drafts' "
            "AND constraint_name = 'uq_fantasy_user_tournament'"
        )).scalar()
        new_constraint = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.table_constraints "
            "WHERE table_schema = DATABASE() AND table_name = 'fantasy_drafts' "
            "AND constraint_name = 'uq_fantasy_user_tournament_series'"
        )).scalar()

        if new_constraint:
            print("Пропущено: уникальный индекс uq_fantasy_user_tournament_series уже существует.")
        else:
            # Новый индекс сначала — MySQL держит tournament_id FK "привязанным"
            # к старому индексу как к опорному и не даёт его дропнуть, пока
            # нет другого индекса с тем же префиксом столбцов на замену.
            conn.execute(text(
                "ALTER TABLE fantasy_drafts "
                "ADD CONSTRAINT uq_fantasy_user_tournament_series "
                "UNIQUE (user_id, tournament_id, tournament_series_id);"
            ))
            conn.commit()
            print("OK: добавлен новый уникальный индекс (user_id, tournament_id, tournament_series_id).")

        # Старый индекс теперь можно спокойно убрать — опорную роль для FK
        # у него уже перехватил новый (тот же префикс user_id, tournament_id).
        old_constraint_still_there = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.table_constraints "
            "WHERE table_schema = DATABASE() AND table_name = 'fantasy_drafts' "
            "AND constraint_name = 'uq_fantasy_user_tournament'"
        )).scalar()
        if old_constraint_still_there:
            conn.execute(text(
                "ALTER TABLE fantasy_drafts DROP INDEX uq_fantasy_user_tournament;"
            ))
            conn.commit()
            print("OK: удалён старый уникальный индекс uq_fantasy_user_tournament.")
        else:
            print("Пропущено: старого индекса uq_fantasy_user_tournament уже нет.")

print("Готово.")
