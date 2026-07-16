"""
Миграция для подтверждённого состава серии турнира.

Запустить один раз на существующей базе:

    python migrate_series_confirmed_players.py

Добавляет колонку tournament_series.confirmed_player_ids (TEXT, nullable,
JSON-список id игроков) — кого админ подтвердил играющими в конкретный
вечер, отдельно от полного состава турнира (tournament_participants).
NULL — состав ещё не объявлен, фэнтези-драфт на эту серию по умолчанию
открыт на весь турнирный ростер (см. FantasyService.get_available_picks).

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
            "AND table_name = 'tournament_series' AND column_name = 'confirmed_player_ids'"
        )).scalar()

        if column_exists:
            print("Пропущено: tournament_series.confirmed_player_ids уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE tournament_series "
                "ADD COLUMN confirmed_player_ids TEXT NULL;"
            ))
            conn.commit()
            print("OK: добавлена колонка tournament_series.confirmed_player_ids.")

print("Готово.")
