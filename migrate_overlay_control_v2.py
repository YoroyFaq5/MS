"""
Миграция: добавляет show_seats и standings_scope в overlay_controls.

Запустить один раз на существующей базе:

    python migrate_overlay_control_v2.py

show_seats (BOOL, default 1) — показывать/скрывать полосу карточек
игроков внизу оверлея, независимо от тикера/таблицы/реванша.

standings_scope (VARCHAR, default 'evening') — для серийных турниров:
'evening' — таблица только текущей серии (вечера), 'series' — общий
зачёт всего турнира целиком. Для обычных (несерийных) турниров
игнорируется.

Безопасно перезапускать: перед каждым ALTER TABLE проверяется текущее
состояние схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        for column, ddl in [
            ("show_seats", "ALTER TABLE overlay_controls ADD COLUMN show_seats TINYINT(1) NOT NULL DEFAULT 1;"),
            ("standings_scope", "ALTER TABLE overlay_controls ADD COLUMN standings_scope VARCHAR(10) NOT NULL DEFAULT 'evening';"),
        ]:
            existing = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = DATABASE() "
                "AND table_name = 'overlay_controls' AND column_name = :col"
            ), {"col": column}).scalar()

            if existing:
                print(f"Пропущено: overlay_controls.{column} уже существует.")
            else:
                conn.execute(text(ddl))
                conn.commit()
                print(f"OK: добавлена колонка overlay_controls.{column}.")

print("Готово.")
