"""
Task 4 — symmetric participant registration/removal: both allowed only for
a 'pending' tournament; both rejected (without touching data) for 'active'
and 'finished'.
"""
from app import db
from app.models import TournamentParticipant
from app.services.tournament_service import TournamentService
from helpers import make_player, make_tournament


def _participant_ids(tournament_id):
    return {
        p.player_id for p in
        db.session.query(TournamentParticipant).filter_by(tournament_id=tournament_id).all()
    }


def test_register_and_remove_allowed_when_pending(app_ctx):
    t = make_tournament("Pending Cup", status="pending")
    p = make_player("Pending Player")

    result = TournamentService.register_participant(t.id, p.id)
    assert result.ok
    assert p.id in _participant_ids(t.id)

    result = TournamentService.remove_participant(t.id, p.id)
    assert result.ok
    assert p.id not in _participant_ids(t.id)


def test_register_rejected_when_active(app_ctx):
    t = make_tournament("Active Cup", status="active")
    p = make_player("Late Joiner")

    result = TournamentService.register_participant(t.id, p.id)
    assert not result.ok
    assert p.id not in _participant_ids(t.id)


def test_remove_rejected_when_active(app_ctx):
    t = make_tournament("Active Cup 2", status="pending")
    p = make_player("Seated Player")
    TournamentService.register_participant(t.id, p.id)
    t.status = "active"
    db.session.commit()

    result = TournamentService.remove_participant(t.id, p.id)
    assert not result.ok
    assert p.id in _participant_ids(t.id), "data must be untouched on rejection"


def test_register_rejected_when_finished(app_ctx):
    t = make_tournament("Finished Cup", status="finished")
    p = make_player("Too Late")

    result = TournamentService.register_participant(t.id, p.id)
    assert not result.ok
    assert p.id not in _participant_ids(t.id)


def test_remove_rejected_when_finished(app_ctx):
    t = make_tournament("Finished Cup 2", status="pending")
    p = make_player("Historic Player")
    TournamentService.register_participant(t.id, p.id)
    t.status = "finished"
    db.session.commit()

    result = TournamentService.remove_participant(t.id, p.id)
    assert not result.ok
    assert p.id in _participant_ids(t.id), "data must be untouched on rejection"
