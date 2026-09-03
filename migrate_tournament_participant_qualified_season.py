"""
Миграция: добавляет tournament_participants.qualified_via_season_id.

Запустить один раз на существующей базе:

    python migrate_tournament_participant_qualified_season.py

qualified_via_season_id (INT NULL, FK -> seasons.id ON DELETE SET NULL) —
происхождение регистрации в турнире для механики «Стол года» (см.
SeasonService._sync_year_tournament_participants / compute_year_qualifiers).
NULL (значение по умолчанию для всех существующих строк) = обычная
регистрация — вручную администратором или неявно через участие в турнирной
игре (games.py::_ensure_tournament_participants). НЕ NULL = эта строка была
добавлена автоматической синхронизацией квалификантов «Стола года» именно
через сезон с этим id — только такие строки повторная синхронизация может
безопасно удалить/переклассифицировать; строка с NULL никогда не трогается.

Безопасно перезапускать: перед ALTER TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "qualified_via_season_id"

        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'tournament_participants' AND column_name = :col"
        ), {"col": column}).scalar()

        if existing:
            print(f"Пропущено: tournament_participants.{column} уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE tournament_participants ADD COLUMN qualified_via_season_id INT NULL;"
            ))
            conn.execute(text(
                "ALTER TABLE tournament_participants "
                "ADD CONSTRAINT fk_tournament_participants_qualified_via_season "
                "FOREIGN KEY (qualified_via_season_id) REFERENCES seasons(id) ON DELETE SET NULL;"
            ))
            conn.commit()
            print(f"OK: добавлена колонка tournament_participants.{column} (+ FK на seasons).")

print("Готово.")
