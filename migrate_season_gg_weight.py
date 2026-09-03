"""
Миграция: добавляет seasons.gg_weight.

Запустить один раз на существующей базе:

    python migrate_season_gg_weight.py

gg_weight (FLOAT NOT NULL DEFAULT 0.2) — вес GG-бонуса в формуле сезонного
рейтинга (SeasonRatingEngine: SeasonRating = TotalPoints*WR% + GG*gg_weight),
зафиксированный НА САМОЙ ЗАПИСИ сезона в момент его создания, а не глобальной
константой. 0.2 по умолчанию для всех существующих строк — уже
существующие/закрытые сезоны навсегда сохраняют старую формулу, их
исторический результат не меняется. SeasonService.ensure_year_exists()
явно проставляет 0.1 любому сезону, созданному после этой миграции.

Безопасно перезапускать: перед ALTER TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "gg_weight"

        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'seasons' AND column_name = :col"
        ), {"col": column}).scalar()

        if existing:
            print(f"Пропущено: seasons.{column} уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE seasons ADD COLUMN gg_weight FLOAT NOT NULL DEFAULT 0.2;"
            ))
            conn.commit()
            print(f"OK: добавлена колонка seasons.{column} (все существующие сезоны = 0.2).")

print("Готово.")
