"""
Tournaments Blueprint
=====================
All view logic delegates to TournamentService / RatingService.
Zero business logic here — only HTTP layer.
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, jsonify
)
from app import db
from app.models import (
    Tournament, TournamentStage, TournamentParticipant,
    Team, TeamPlayer, Game, GameSlot, Player, Role,
    TournamentType, StageType, SeriesTournament,
)
from app.services import TournamentService, RatingService
from app.services.shop_service import ShopService
from app.auth_decorators import admin_required

tournaments_bp = Blueprint("tournaments", __name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_tournament_or_404(tournament_id: int) -> Tournament:
    return db.session.get(Tournament, tournament_id) or abort(404)


def _get_stage_or_404(stage_id: int) -> TournamentStage:
    return db.session.get(TournamentStage, stage_id) or abort(404)


def _active_players():
    return db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()


def _get_series_tournament_id(tournament_id: int) -> int | None:
    """
    A series-tournament is just a Tournament row with a matching
    SeriesTournament wrapper (see series_tournament_service.py). Bracket
    actions (cutoff, whole-pool "next round", generic "finish stage") make
    no sense for a series' evenings and can silently corrupt state (e.g.
    run_cutoff marks advanced_to_final from a single evening's rating,
    then finds no FINAL stage to activate) — routes/templates use this to
    hide those actions and point admins to /series-tournaments/... instead.
    """
    st = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()
    return st.id if st else None


# ── Tournament CRUD ───────────────────────────────────────────────────────────

@tournaments_bp.route("/")
def list_tournaments():
    tournaments = (
        db.session.query(Tournament)
        .order_by(Tournament.created_at.desc())
        .all()
    )
    series_tournament_ids = {
        st.tournament_id: st.id
        for st in db.session.query(SeriesTournament).all()
    }
    return render_template(
        "tournaments/list.html",
        tournaments=tournaments,
        series_tournament_ids=series_tournament_ids,
    )


@tournaments_bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_tournament():
    if request.method == "POST":
        t_type_str = request.form.get("type", "individual")
        try:
            t_type = TournamentType(t_type_str)
        except ValueError:
            t_type = TournamentType.INDIVIDUAL

        result = TournamentService.create_tournament(
            name=request.form.get("name", ""),
            t_type=t_type,
            is_ranked=bool(request.form.get("is_ranked")),
            has_stages=bool(request.form.get("has_stages")),
            cutoff_size=int(request.form.get("cutoff_size", 10) or 10),
            description=request.form.get("description", ""),
        )
        if result.ok:
            flash(result.message, "success")
            return redirect(url_for("tournaments.tournament_detail", tournament_id=result.data.id))
        flash(result.message, "danger")

    return render_template("tournaments/form.html")


@tournaments_bp.route("/<int:tournament_id>")
def tournament_detail(tournament_id: int):
    summary = TournamentService.get_tournament_summary(tournament_id)
    if not summary:
        abort(404)
    all_players = _active_players()
    # Players not yet in this tournament
    registered_ids = {p.player_id for p in summary["tournament"].participants}
    available_players = [p for p in all_players if p.id not in registered_ids]

    player_ids = set(registered_ids)
    player_ids.update(r.player_id for r in summary["player_ratings"])
    for team in summary["tournament"].teams:
        player_ids.update(m.player_id for m in team.members)
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "tournaments/detail.html",
        **summary,
        available_players=available_players,
        registered_ids=list(registered_ids),
        equipped_bulk=equipped_bulk,
        series_tournament_id=_get_series_tournament_id(tournament_id),
    )


@tournaments_bp.route("/<int:tournament_id>/toggle-ranked", methods=["POST"])
@admin_required
def toggle_ranked(tournament_id: int):
    """
    Флаг is_ranked на Tournament — это шаблон "по умолчанию" для НОВЫХ
    игр этого турнира (см. games.py::new_game/_apply_tournament_assignment,
    которые копируют его в Game.is_ranked в момент создания/сохранения
    игры), а не живое свойство, которое переносится на уже существующие
    записи само по себе. Переключение здесь сразу подхватят новые игры и
    уже созданные незавершённые (при их завершении); уже завершённые игры
    сохранят свой прежний снимок is_ranked, пока их не пересохранят через
    режим редактирования — предупреждаем об этом прямо в сообщении.
    """
    t = _get_tournament_or_404(tournament_id)
    t.is_ranked = not t.is_ranked
    db.session.commit()
    flash(
        f"Турнир «{t.name}» теперь "
        f"{'рейтинговый 📈' if t.is_ranked else 'нерейтинговый 🏖'}. "
        f"Уже завершённые игры сохраняют старое значение — поменяется только "
        f"у новых и у пересохранённых через редактирование.",
        "success",
    )
    return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))


@tournaments_bp.route("/<int:tournament_id>/delete", methods=["POST"])
@admin_required
def delete_tournament(tournament_id: int):
    t = _get_tournament_or_404(tournament_id)
    if t.status == "active":
        flash("Нельзя удалить активный турнир. Сначала завершите его.", "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))
    db.session.delete(t)
    db.session.commit()
    flash(f"Турнир «{t.name}» удалён.", "info")
    return redirect(url_for("tournaments.list_tournaments"))


# ── Lifecycle actions ─────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/activate", methods=["POST"])
@admin_required
def activate_tournament(tournament_id: int):
    result = TournamentService.activate_tournament(tournament_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))


@tournaments_bp.route("/<int:tournament_id>/finish", methods=["POST"])
@admin_required
def finish_tournament(tournament_id: int):
    result = TournamentService.finish_tournament(tournament_id)
    if not result.ok:
        flash(result.message, "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    # Run full post-tournament pipeline: fantasy scoring + coin rewards + season update
    from app.services.orchestrator import PostTournamentOrchestrator
    tournament = db.session.get(Tournament, tournament_id)
    orch = PostTournamentOrchestrator.run(tournament)

    if orch.errors:
        flash(
            f"Турнир завершён, но возникли предупреждения: {'; '.join(orch.errors)}",
            "warning"
        )
    else:
        flash(
            f"Турнир завершён! Начислены монеты и подсчитаны Fantasy-очки. "
            f"Шагов выполнено: {len(orch.steps)}.",
            "success"
        )
    return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))


# ── Participants ──────────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/participants/add", methods=["POST"])
@admin_required
def add_participant(tournament_id: int):
    player_id = request.form.get("player_id", type=int)
    if not player_id:
        flash("Игрок не выбран.", "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))
    result = TournamentService.register_participant(tournament_id, player_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))


@tournaments_bp.route("/<int:tournament_id>/participants/<int:player_id>/remove", methods=["POST"])
@admin_required
def remove_participant(tournament_id: int, player_id: int):
    result = TournamentService.remove_participant(tournament_id, player_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))


# ── Stages ────────────────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/stages")
def stages(tournament_id: int):
    t = _get_tournament_or_404(tournament_id)
    sorted_stages = sorted(t.stages, key=lambda s: s.order)
    stage_ratings = {}
    for s in sorted_stages:
        stage_ratings[s.id] = RatingService.get_stage_rating(s.id)

    player_ids = {r.player_id for ratings in stage_ratings.values() for r in ratings}
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "tournaments/stages.html",
        tournament=t,
        stages=sorted_stages,
        stage_ratings=stage_ratings,
        equipped_bulk=equipped_bulk,
        series_tournament_id=_get_series_tournament_id(tournament_id),
    )


@tournaments_bp.route("/<int:tournament_id>/stages/add", methods=["POST"])
@admin_required
def add_stage(tournament_id: int):
    name = request.form.get("name", "").strip()
    stage_type_str = request.form.get("stage_type", "main")
    try:
        stage_type = StageType(stage_type_str)
    except ValueError:
        stage_type = StageType.MAIN

    result = TournamentService.add_stage(tournament_id, name, stage_type)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.stages", tournament_id=tournament_id))


@tournaments_bp.route("/stages/<int:stage_id>/activate", methods=["POST"])
@admin_required
def activate_stage(stage_id: int):
    stage = _get_stage_or_404(stage_id)
    result = TournamentService.activate_stage(stage_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.stages", tournament_id=stage.tournament_id))


_SERIES_ACTION_BLOCKED_MSG = (
    "Это серийный турнир — управляйте его сериями (вечерами) через "
    "страницу серийного турнира, а не через общие действия с этапами."
)


@tournaments_bp.route("/stages/<int:stage_id>/finish", methods=["POST"])
@admin_required
def finish_stage(stage_id: int):
    stage = _get_stage_or_404(stage_id)
    if _get_series_tournament_id(stage.tournament_id):
        flash(_SERIES_ACTION_BLOCKED_MSG, "danger")
        return redirect(url_for("tournaments.stages", tournament_id=stage.tournament_id))
    result = TournamentService.finish_stage(stage_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.stages", tournament_id=stage.tournament_id))


@tournaments_bp.route("/stages/<int:stage_id>/cutoff", methods=["POST"])
@admin_required
def run_cutoff(stage_id: int):
    stage = _get_stage_or_404(stage_id)
    if _get_series_tournament_id(stage.tournament_id):
        flash(_SERIES_ACTION_BLOCKED_MSG, "danger")
        return redirect(url_for("tournaments.stages", tournament_id=stage.tournament_id))
    result = TournamentService.run_cutoff(stage_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.leaderboard", tournament_id=stage.tournament_id))


@tournaments_bp.route("/stages/<int:stage_id>/next-round", methods=["POST"])
@admin_required
def generate_next_round(stage_id: int):
    stage = _get_stage_or_404(stage_id)
    if _get_series_tournament_id(stage.tournament_id):
        flash(_SERIES_ACTION_BLOCKED_MSG, "danger")
        return redirect(url_for("tournaments.stages", tournament_id=stage.tournament_id))
    result = TournamentService.generate_next_round(stage_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.tournament_games", tournament_id=stage.tournament_id))


# ── Leaderboard ───────────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/leaderboard")
def leaderboard(tournament_id: int):
    t = _get_tournament_or_404(tournament_id)
    player_ratings = RatingService.get_tournament_rating(tournament_id)
    team_ratings = (
        RatingService.get_team_rating(tournament_id)
        if t.type == TournamentType.TEAM else []
    )
    final_participants = TournamentService.get_final_stage_participants(tournament_id)
    final_ids = {p.player_id for p in final_participants}

    from app.services import TitleService
    player_ids = [r.player_id for r in player_ratings]
    equipped_titles = TitleService.get_equipped_titles_bulk(player_ids)
    equipped_bulk = ShopService.get_equipped_bulk(player_ids)

    return render_template(
        "tournaments/leaderboard.html",
        tournament=t,
        player_ratings=player_ratings,
        team_ratings=team_ratings,
        final_ids=final_ids,
        equipped_titles=equipped_titles,
        equipped_bulk=equipped_bulk,
    )


# ── Final bracket ─────────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/final")
def final_view(tournament_id: int):
    t = _get_tournament_or_404(tournament_id)
    final_stage = next(
        (s for s in sorted(t.stages, key=lambda s: s.order)
         if s.type == StageType.FINAL),
        None,
    )
    if not final_stage:
        flash("Финальный этап не найден.", "warning")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))

    final_ratings = RatingService.get_stage_rating(final_stage.id)
    final_games = sorted(final_stage.games, key=lambda g: g.played_at, reverse=True)
    final_participants = TournamentService.get_final_stage_participants(tournament_id)

    player_ids = {r.player_id for r in final_ratings}
    player_ids.update(fp.player_id for fp in final_participants)
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "tournaments/final.html",
        tournament=t,
        final_stage=final_stage,
        final_ratings=final_ratings,
        final_games=final_games,
        final_participants=final_participants,
        equipped_bulk=equipped_bulk,
    )


# ── Teams ─────────────────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/teams/add", methods=["POST"])
@admin_required
def add_team(tournament_id: int):
    name = request.form.get("name", "")
    color = request.form.get("color") or None
    result = TournamentService.create_team(tournament_id, name, color)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))


@tournaments_bp.route("/teams/<int:team_id>/players/add", methods=["POST"])
@admin_required
def add_team_player(team_id: int):
    team = db.session.get(Team, team_id) or abort(404)
    player_id = request.form.get("player_id", type=int)
    if not player_id:
        flash("Игрок не выбран.", "danger")
        return redirect(url_for("tournaments.tournament_detail", tournament_id=team.tournament_id))
    result = TournamentService.add_player_to_team(team_id, player_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.tournament_detail", tournament_id=team.tournament_id))


@tournaments_bp.route("/teams/<int:team_id>/players/<int:player_id>/remove", methods=["POST"])
@admin_required
def remove_team_player(team_id: int, player_id: int):
    team = db.session.get(Team, team_id) or abort(404)
    tp = db.session.query(TeamPlayer).filter_by(team_id=team_id, player_id=player_id).first()
    if tp:
        db.session.delete(tp)
        # Also clear team_id from participant record
        part = db.session.query(TournamentParticipant).filter_by(
            tournament_id=team.tournament_id, player_id=player_id
        ).first()
        if part:
            part.team_id = None
        db.session.commit()
        flash("Игрок убран из команды.", "info")
    else:
        flash("Игрок не найден в команде.", "danger")
    return redirect(url_for("tournaments.tournament_detail", tournament_id=team.tournament_id))


# ── Generate games ───────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/games/generate", methods=["POST"])
@admin_required
def generate_games(tournament_id: int):
    if _get_series_tournament_id(tournament_id):
        flash(_SERIES_ACTION_BLOCKED_MSG, "danger")
        return redirect(url_for("tournaments.tournament_games", tournament_id=tournament_id))

    n = request.form.get("n_games", type=int, default=1)
    stage_id = request.form.get("stage_id", type=int) or None

    result = TournamentService.generate_games(tournament_id, n or 1, stage_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("tournaments.tournament_games", tournament_id=tournament_id))


# ── Games in tournament ─────────────────────────────────────────────────────────

@tournaments_bp.route("/<int:tournament_id>/games")
def tournament_games(tournament_id: int):
    t = _get_tournament_or_404(tournament_id)
    games = sorted(t.games, key=lambda g: g.id)
    return render_template(
        "tournaments/games.html",
        tournament=t,
        games=games,
    )


# ════════════════════════════════════════════════════════════════════════
# JSON API
# ════════════════════════════════════════════════════════════════════════

@tournaments_bp.route("/api")
def api_list():
    tournaments = db.session.query(Tournament).order_by(Tournament.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tournaments])


@tournaments_bp.route("/api/<int:tournament_id>")
def api_detail(tournament_id: int):
    t = _get_tournament_or_404(tournament_id)
    data = t.to_dict()
    data["stages"] = [s.to_dict() for s in sorted(t.stages, key=lambda s: s.order)]
    data["participant_count"] = len(t.participants)
    return jsonify(data)


@tournaments_bp.route("/api/<int:tournament_id>/stages")
def api_stages(tournament_id: int):
    t = _get_tournament_or_404(tournament_id)
    return jsonify([s.to_dict() for s in sorted(t.stages, key=lambda s: s.order)])


@tournaments_bp.route("/api/<int:tournament_id>/ratings")
def api_ratings(tournament_id: int):
    player_ratings = RatingService.get_tournament_rating(tournament_id)
    t = _get_tournament_or_404(tournament_id)
    team_ratings = (
        RatingService.get_team_rating(tournament_id)
        if t.type == TournamentType.TEAM else []
    )
    return jsonify({
        "players": [r.to_dict() for r in player_ratings],
        "teams": [r.to_dict() for r in team_ratings],
    })
