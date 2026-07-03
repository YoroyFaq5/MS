from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, jsonify
)
from app import db
from app.models import Game, GameSlot, Player, Role, WinSide, Tournament, TournamentStage, StageType, Team, TeamPlayer, TournamentParticipant
from app.services import RatingService
from app.services.season_service import SeasonService
from app.services.shop_service import ShopService
from app.auth_decorators import admin_required

games_bp = Blueprint("games", __name__)

TOTAL_PLAYERS = 10


def _active_players():
    return db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()


def _active_tournaments():
    return (
        db.session.query(Tournament)
        .filter(Tournament.status.in_(["pending", "active"]))
        .order_by(Tournament.name)
        .all()
    )


def _new_game_form_context(tournaments, preselect_tournament=None, preselect_stage=None) -> dict:
    """
    Общий контекст для games/new.html — используется и на GET, и во всех
    веток POST, которые возвращают форму повторно (ошибка валидации).
    Раньше часть таких веток не передавала team_membership/team_names/
    tournament_participants, из-за чего `{{ team_membership | tojson }}`
    в шаблоне падал на Undefined — теперь контекст всегда полный.
    """
    team_membership = {}
    team_names = {}
    tournament_participants = {}

    for t in tournaments:
        parts = db.session.query(TournamentParticipant).filter_by(tournament_id=t.id).all()
        tournament_participants[t.id] = [p.player_id for p in parts]

        if t.type.value == "team":
            mapping = {}
            for team in t.teams:
                team_names[team.id] = team.name
                for member in team.members:
                    mapping[member.player_id] = team.id
            team_membership[t.id] = mapping

    return {
        "preselect_tournament": preselect_tournament,
        "preselect_stage": preselect_stage,
        "team_membership": team_membership,
        "team_names": team_names,
        "tournament_participants": tournament_participants,
    }


# ── Public: просмотр ──────────────────────────────────────────────────────────

@games_bp.route("/")
def list_games():
    games = db.session.query(Game).order_by(Game.played_at.desc()).all()
    return render_template("games/list.html", games=games)


@games_bp.route("/<int:game_id>")
def game_detail(game_id: int):
    game = db.session.get(Game, game_id) or abort(404)
    slots = sorted(game.slots, key=lambda s: s.seat_number)
    # Generated games have all roles as CIVILIAN placeholder — roles are editable
    roles_editable = (
        not game.is_finished and
        all(s.role.value == "civilian" for s in slots) and
        len(slots) == 10
    )
    equipped_bulk = ShopService.get_equipped_bulk([s.player_id for s in slots])
    return render_template("games/detail.html", game=game, slots=slots,
                           roles_editable=roles_editable, equipped_bulk=equipped_bulk)


@games_bp.route("/api/<int:game_id>")
def api_game(game_id: int):
    game = db.session.get(Game, game_id) or abort(404)
    data = game.to_dict()
    data["slots"] = [s.to_dict() for s in sorted(game.slots, key=lambda s: s.seat_number)]
    return jsonify(data)


# ── Admin only: создание / завершение / удаление ──────────────────────────────

@games_bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_game():
    players = _active_players()
    tournaments = _active_tournaments()

    if request.method == "POST":
        if len(players) < TOTAL_PLAYERS:
            flash(f"Нужно минимум {TOTAL_PLAYERS} активных игроков.", "danger")
            return redirect(url_for("games.new_game"))

        notes = request.form.get("notes", "").strip() or None
        tournament_id = request.form.get("tournament_id", type=int) or None
        stage_id = request.form.get("stage_id", type=int) or None

        is_ranked = True
        t = None
        if tournament_id:
            t = db.session.get(Tournament, tournament_id)
            if t:
                is_ranked = t.is_ranked
            if stage_id:
                stage = db.session.get(TournamentStage, stage_id)
                if not stage or stage.tournament_id != tournament_id:
                    flash("Этап не принадлежит выбранному турниру.", "danger")
                    return render_template(
                        "games/new.html", players=players, tournaments=tournaments,
                        **_new_game_form_context(tournaments, tournament_id, stage_id),
                    )
                if stage.status != "active":
                    flash(f"Этап «{stage.name}» не активен.", "danger")
                    return render_template(
                        "games/new.html", players=players, tournaments=tournaments,
                        **_new_game_form_context(tournaments, tournament_id, stage_id),
                    )

        # Validate all players are tournament participants (if game is in a tournament)
        if tournament_id and t:
            participant_ids = {
                p.player_id for p in
                db.session.query(TournamentParticipant).filter_by(tournament_id=tournament_id).all()
            }
            if participant_ids:  # only validate if tournament has registered participants
                non_members = []
                for seat in range(1, TOTAL_PLAYERS + 1):
                    pid_str = request.form.get(f"player_{seat}")
                    if pid_str:
                        try:
                            pid = int(pid_str)
                        except ValueError:
                            continue
                        if pid not in participant_ids:
                            player_obj = db.session.get(Player, pid)
                            name = player_obj.display_name if player_obj else str(pid)
                            non_members.append(name)
                if non_members:
                    flash(
                        f"Игроки не являются участниками турнира: {', '.join(non_members)}. "
                        f"Сначала добавьте их в турнир.",
                        "danger"
                    )
                    return render_template(
                        "games/new.html", players=players, tournaments=tournaments,
                        **_new_game_form_context(tournaments, tournament_id, stage_id),
                    )

        # Team conflict check
        selected_ids_pre = []
        for seat in range(1, TOTAL_PLAYERS + 1):
            pid_str = request.form.get(f"player_{seat}")
            if pid_str:
                try:
                    selected_ids_pre.append(int(pid_str))
                except ValueError:
                    pass

        if tournament_id and t and t.type.value == "team":
            team_hits: dict[int, list[str]] = {}
            for pid in selected_ids_pre:
                tp = (
                    db.session.query(TeamPlayer)
                    .join(Team)
                    .filter(Team.tournament_id == tournament_id, TeamPlayer.player_id == pid)
                    .first()
                )
                if tp:
                    player = db.session.get(Player, pid)
                    team_hits.setdefault(tp.team_id, []).append(
                        player.display_name if player else str(pid)
                    )
            conflicts = [
                f"Команда «{db.session.get(Team, tid).name}»: {', '.join(names)}"
                for tid, names in team_hits.items() if len(names) > 1
            ]
            if conflicts:
                for c in conflicts:
                    flash(f"Конфликт состава — {c} не могут играть вместе.", "danger")
                return render_template(
                    "games/new.html", players=players, tournaments=tournaments,
                    **_new_game_form_context(tournaments, tournament_id, stage_id),
                )

        game = Game(notes=notes, tournament_id=tournament_id, stage_id=stage_id, is_ranked=is_ranked)
        db.session.add(game)
        db.session.flush()

        errors = []
        selected_ids = []
        for seat in range(1, TOTAL_PLAYERS + 1):
            pid_str = request.form.get(f"player_{seat}")
            role_str = request.form.get(f"role_{seat}")
            if not pid_str or not role_str:
                errors.append(f"Место {seat}: игрок и роль обязательны.")
                continue
            try:
                pid = int(pid_str)
                role = Role(role_str)
            except (ValueError, KeyError):
                errors.append(f"Место {seat}: неверные данные.")
                continue
            if pid in selected_ids:
                errors.append(f"Игрок #{pid} выбран дважды.")
            selected_ids.append(pid)
            db.session.add(GameSlot(
                game_id=game.id, player_id=pid,
                seat_number=seat, role=role,
                base_score=0.0, bonus_score=0.0,
            ))

        if errors:
            db.session.rollback()
            for e in errors:
                flash(e, "danger")
            return render_template(
                "games/new.html", players=players, tournaments=tournaments,
                **_new_game_form_context(tournaments, tournament_id, stage_id),
            )

        db.session.commit()
        SeasonService.resolve_season_for_game(game)
        db.session.commit()

        flash("Игра создана! Заполните бонусы и завершите игру.", "success")
        return redirect(url_for("games.game_detail", game_id=game.id))

    preselect_tournament = request.args.get("tournament_id", type=int)
    preselect_stage = request.args.get("stage_id", type=int)

    return render_template(
        "games/new.html",
        players=players,
        tournaments=tournaments,
        **_new_game_form_context(tournaments, preselect_tournament, preselect_stage),
    )


@games_bp.route("/<int:game_id>/finish", methods=["POST"])
@admin_required
def finish_game(game_id: int):
    game = db.session.get(Game, game_id) or abort(404)

    if game.is_finished:
        flash("Игра уже завершена.", "warning")
        return redirect(url_for("games.game_detail", game_id=game_id))

    win_side_str = request.form.get("win_side", "none")
    try:
        game.win_side = WinSide(win_side_str)
    except ValueError:
        flash("Неверное значение победителя.", "danger")
        return redirect(url_for("games.game_detail", game_id=game_id))

    # ── Apply all per-slot values from form ─────────────────────────────────
    for slot in game.slots:
        # Role (editable for generated games where all roles are placeholder)
        role_val = request.form.get(f"role_{slot.id}", "").strip()
        if role_val:
            try:
                slot.role = Role(role_val)
            except ValueError:
                pass

        # Bonus score
        val = request.form.get(f"bonus_{slot.id}", "0").strip()
        try:
            slot.bonus_score = float(val)
        except ValueError:
            slot.bonus_score = 0.0

        # PU flag (Первый Убиенный)
        slot.is_pu = bool(request.form.get(f"pu_{slot.id}"))
        if slot.is_pu:
            try:
                slot.pu_mafia_count = max(0, min(3, int(
                    request.form.get(f"pu_mafia_{slot.id}", 0)
                )))
            except ValueError:
                slot.pu_mafia_count = 0
        else:
            slot.pu_mafia_count = 0

        # Quality score (optional, -1..+1)
        qs_val = request.form.get(f"quality_{slot.id}", "").strip()
        if qs_val:
            try:
                slot.quality_score = max(-1.0, min(1.0, float(qs_val)))
            except ValueError:
                pass

    # ── Validate role distribution ────────────────────────────────────────────
    from collections import Counter
    role_dist = Counter(s.role.value for s in game.slots)
    if all(s.role.value == "civilian" for s in game.slots):
        flash("Назначьте роли перед завершением игры (сейчас все — Мирный).", "danger")
        return redirect(url_for("games.game_detail", game_id=game_id))
    if role_dist.get("mafia", 0) + role_dist.get("don", 0) == 0:
        flash("В игре должна быть хотя бы одна роль мафии (Мафия или Дон).", "danger")
        return redirect(url_for("games.game_detail", game_id=game_id))

    game.is_finished = True
    db.session.flush()

    from app.services.orchestrator import PostGameOrchestrator
    orch = PostGameOrchestrator.run(game)
    if orch.errors:
        flash(f"Завершено с предупреждениями: {'; '.join(orch.errors)}", "warning")
    else:
        flash("Игра завершена! Рейтинг и монеты обновлены.", "success")

    if game.tournament_id:
        return redirect(url_for("tournaments.tournament_detail", tournament_id=game.tournament_id))
    return redirect(url_for("games.game_detail", game_id=game_id))


@games_bp.route("/<int:game_id>/delete", methods=["POST"])
@admin_required
def delete_game(game_id: int):
    game = db.session.get(Game, game_id) or abort(404)
    tournament_id = game.tournament_id
    db.session.delete(game)
    db.session.commit()
    flash("Игра удалена.", "info")
    if tournament_id:
        return redirect(url_for("tournaments.tournament_detail", tournament_id=tournament_id))
    return redirect(url_for("games.list_games"))
