"""
Миграция: добавляет game_slots.credit_team_id.

Запустить один раз на существующей базе:

    python migrate_credit_team_id.py

credit_team_id (INT NULL, FK -> teams.id, ON DELETE SET NULL) — "в чью
пользу идёт результат этого места", отдельно от того, кто физически
сидит (player_id). Для обычной командной игры совпадает с командой
сидящего игрока; расходится, когда за команду в раунде сыграл
посторонний игрок клуба "на замену" — его результат должен уйти в
зачёт команды, хотя сам он не её участник. См. TournamentService.
generate_next_team_round и RatingService.get_team_rating.

NULL по умолчанию для всех существующих строк — старые командные
турниры, никогда не тронутые новым механизмом, продолжают считаться
через TeamPlayer/TournamentParticipant.team_id как раньше (get_team_rating
падает на старый путь, когда credit_team_id не проставлен).

Безопасно перезапускать: перед ALTER TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "credit_team_id"

        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'game_slots' AND column_name = :col"
        ), {"col": column}).scalar()

        if existing:
            print(f"Пропущено: game_slots.{column} уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE game_slots ADD COLUMN credit_team_id INT NULL;"
            ))
            conn.execute(text(
                "ALTER TABLE game_slots ADD CONSTRAINT fk_game_slots_credit_team "
                "FOREIGN KEY (credit_team_id) REFERENCES teams(id) ON DELETE SET NULL;"
            ))
            conn.commit()
            print(f"OK: добавлена колонка game_slots.{column} (+ FK на teams).")

print("Готово.")
