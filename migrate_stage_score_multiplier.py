"""
Миграция: добавляет tournament_stages.score_multiplier.

Запустить один раз на существующей базе:

    python migrate_stage_score_multiplier.py

score_multiplier (FLOAT NOT NULL DEFAULT 1) — коэффициент, на который
умножаются очки GameSlot.total_score за игры этого этапа при подсчёте
турнирной/этапной таблицы (RatingService.get_tournament_rating/
get_stage_rating/get_team_rating). 1.0 по умолчанию для всех существующих
строк — старые турниры/этапы продолжают считаться как раньше, механика
даёт эффект только там, где админ явно поставил значение != 1. НЕ влияет
на общий сайтовый рейтинг (compute_all_ratings) — см. TournamentStage.

Безопасно перезапускать: перед ALTER TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "score_multiplier"

        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'tournament_stages' AND column_name = :col"
        ), {"col": column}).scalar()

        if existing:
            print(f"Пропущено: tournament_stages.{column} уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE tournament_stages "
                "ADD COLUMN score_multiplier FLOAT NOT NULL DEFAULT 1;"
            ))
            conn.commit()
            print(f"OK: добавлена колонка tournament_stages.{column}.")

print("Готово.")
