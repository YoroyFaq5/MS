"""
Миграция для скрытия таблицы очков/итоговых мест турнира.

Запустить один раз на существующей базе:

    python migrate_tournament_hide_standings.py

Добавляет колонку tournaments.hide_standings (BOOL, NOT NULL, default 0) —
админ может скрыть таблицу рейтинга турнира (очки, места, ELO и т.п.) от
всех, кроме админов, которые сами не участвуют в этом турнире (см.
app/routes/tournaments.py::_can_view_standings).

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
            "AND table_name = 'tournaments' AND column_name = 'hide_standings'"
        )).scalar()

        if existing:
            print("Пропущено: tournaments.hide_standings уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE tournaments "
                "ADD COLUMN hide_standings TINYINT(1) NOT NULL DEFAULT 0;"
            ))
            conn.commit()
            print("OK: добавлена колонка tournaments.hide_standings.")

print("Готово.")
