"""
Разовый фикс данных: в играх 1387, 1389, 1390 место 1 было по ошибке
привязано к уже существующему игроку «Олег Олегович» (id=213), хотя на
самом деле это был совсем новый человек, пришедший через вебхук
MafiaSpace — админ при разборе очереди /admin/imports перепутал его с
существующим тёзкой.

Запустить ОДИН РАЗ на проде:

    python fix_oleg_olegovich_player.py

Делает: бэкап Player.elo в /root/oleg_fix_elo_backup.tsv, заводит нового
игрока «ОлеГЫч», переносит место 1 в играх 1387/1390/1389 на него,
пересчитывает ELO/монеты через EditGameOrchestrator (та же логика, что и
у ручного редактирования игры), и перепривязывает ExternalPlayerLink на
нового игрока — чтобы будущие игры этого же человека из MafiaSpace
больше не путались с «Олег Олегович».

НЕ идемпотентен — при повторном запуске упадёт на втором проходе
(слоты уже не принадлежат player_id=213), это ожидаемо и безопасно
(ничего не задваивает).
"""
from app import create_app, db
from app.models import Player, Game, ExternalPlayerLink
from app.services.orchestrator import EditGameOrchestrator

app = create_app('production')
with app.app_context():
    old_player = db.session.get(Player, 213)
    print('old player:', old_player.id, old_player.nickname, 'elo=', old_player.elo)
    assert old_player.nickname == 'Олег Олегович', 'nickname mismatch, aborting'

    with open('/root/oleg_fix_elo_backup.tsv', 'w', encoding='utf-8') as f:
        f.write('id\telo\n')
        for p in db.session.query(Player).all():
            f.write(f'{p.id}\t{p.elo}\n')
    print('backup written to /root/oleg_fix_elo_backup.tsv')

    new_player = Player(nickname='ОлеГЫч', name='ОлеГЫч')
    db.session.add(new_player)
    db.session.flush()
    print('created new player id=', new_player.id, new_player.nickname)

    game_ids = [1387, 1390, 1389]
    for gid in game_ids:
        game = db.session.get(Game, gid)
        old_player_ids = [s.player_id for s in game.slots]
        slot = next(s for s in game.slots if s.player_id == 213)
        slot.player_id = new_player.id
        db.session.flush()
        result = EditGameOrchestrator.run(game, old_player_ids, game.tournament_id, game.stage_id)
        print(f'game {gid}: reassigned seat {slot.seat_number}, errors={result.errors}')

    links = db.session.query(ExternalPlayerLink).filter_by(player_id=213).all()
    print(f'found {len(links)} ExternalPlayerLink(s) pointing at old player 213:')
    for link in links:
        print(' ', link.source, link.external_id, '-> repointing to new player', new_player.id)
        link.player_id = new_player.id
    db.session.commit()

    print('--- RESULT ---')
    print('old player (Олег Олегович) elo now:', db.session.get(Player, 213).elo)
    print('new player (ОлеГЫч) id=', new_player.id, 'elo now:', db.session.get(Player, new_player.id).elo)
