"""
Миграция: добавляет idle_content в overlay_controls.

Запустить один раз на существующей базе:

    python migrate_overlay_control_v3.py

idle_content (VARCHAR, default 'logo') — что показывать в центральном
блоке экрана ожидания (Live, но текущей игры ещё нет): 'logo' (лого +
название турнира), 'standings' (турнирная таблица), 'last_game'
(карточка прошлой игры), 'ticker' (интересные факты турнира).

Безопасно перезапускать: перед ALTER TABLE проверяется текущее
состояние схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "idle_content"
        ddl = "ALTER TABLE overlay_controls ADD COLUMN idle_content VARCHAR(10) NOT NULL DEFAULT 'logo';"

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
