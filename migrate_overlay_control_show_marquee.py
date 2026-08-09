"""
Миграция: добавляет show_marquee в overlay_controls.

Запустить один раз на существующей базе:

    python migrate_overlay_control_show_marquee.py

show_marquee (BOOLEAN NOT NULL DEFAULT TRUE) — независимый тумблер
бегущей строки со статистикой турнира (низ страницы Live-Комментаторы,
см. marquee_stats в overlay.py). По умолчанию включена — как и
show_ticker/show_seats, ничего не меняется для уже идущих трансляций,
пока админ явно её не скроет.

Безопасно перезапускать: перед ALTER TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "show_marquee"

        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'overlay_controls' AND column_name = :col"
        ), {"col": column}).scalar()

        if existing:
            print(f"Пропущено: overlay_controls.{column} уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE overlay_controls ADD COLUMN show_marquee "
                "BOOLEAN NOT NULL DEFAULT TRUE;"
            ))
            conn.commit()
            print(f"OK: добавлена колонка overlay_controls.{column}.")

print("Готово.")
