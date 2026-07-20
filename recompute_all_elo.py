"""
Полный пересчёт ELO всех игроков с нуля по обновлённой формуле EloEngine
(E_i теперь считается от ИНДИВИДУАЛЬНОГО ELO игрока против среднего
соперника, а не от среднего его же команды; veteran dampening смягчён:
порог 100→150 игр, коэффициент 0.65→0.8 — см. app/services/elo_engine.py).

Запустить один раз после обновления констант:

    python recompute_all_elo.py

Сбрасывает ELO всех игроков, когда-либо участвовавших в ранговой
завершённой игре, на 1000.0, затем реплеит ВСЕ такие игры в
хронологическом порядке через EloEngine.apply_match() — это одновременно
пересчитывает elo_after на каждом слоте (график истории ELO тоже
обновится корректно).

Безопасно перезапускать — детерминированный пересчёт с нуля, не
полагается на текущие значения Player.elo.
"""
from app import create_app, db
from app.models import Player, Game
from app.services.elo_engine import EloEngine

app = create_app("development")

with app.app_context():
    games = (
        db.session.query(Game)
        .filter(Game.is_finished == True, Game.is_ranked == True)
        .order_by(Game.played_at.asc(), Game.id.asc())
        .all()
    )
    print(f"Найдено {len(games)} ранговых завершённых игр.")

    player_ids = set()
    for g in games:
        player_ids.update(s.player_id for s in g.slots)
    print(f"Затронуто {len(player_ids)} игроков — сбрасываю ELO на 1000.")

    for pid in player_ids:
        player = db.session.get(Player, pid)
        if player:
            player.elo = 1000.0
            db.session.add(player)
    db.session.flush()

    for i, g in enumerate(games, start=1):
        EloEngine.apply_match(g, commit=False)
        if i % 200 == 0:
            print(f"  ...{i}/{len(games)} игр пересчитано")

    db.session.commit()
    print("Готово — ELO всех игроков пересчитан по новой формуле.")
