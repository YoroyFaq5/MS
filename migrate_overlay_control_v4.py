"""
Миграция: добавляет layout_mode в overlay_controls.

Запустить один раз на существующей базе:

    python migrate_overlay_control_v4.py

layout_mode (VARCHAR, default 'game') — какой макет живого эфира сейчас
показывать, выбирается вручную админом (не зависит от того, есть ли
current_game): 'commentators' — экран ожидания с плейсхолдерами под
комментатора/чат и переключаемым центральным блоком (idle_content);
'game' — обычная полоса карточек игроков внизу (текущая игра, либо
полоса "Ожидание начала игры", если её нет), без плейсхолдеров.
Тикер/таблица в углах не зависят от этого переключателя.

Default 'game' сохраняет текущее поведение для уже идущих трансляций —
экран с комментаторами админ включает вручную, когда нужно.

Безопасно перезапускать: перед ALTER TABLE проверяется текущее
состояние схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "layout_mode"
        ddl = "ALTER TABLE overlay_controls ADD COLUMN layout_mode VARCHAR(12) NOT NULL DEFAULT 'game';"

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
