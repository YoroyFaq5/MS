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


def _notify_next_slot(round_data: dict) -> None:
    """
    Fire-and-forget уведомление боту о новой рассадке — только для
    игроков, у которых привязан Telegram (Player.telegram_id). Отсутствие
    привязки у части/всех игроков — не ошибка, их просто пропускаем.
    """
    assignments = round_data.get("assignments") or []
    if not assignments:
        return

    player_ids = {a["player_id"] for a in assignments}
    telegram_ids = {
        p.id: p.telegram_id
        for p in db.session.query(Player).filter(Player.id.in_(player_ids)).all()
        if p.telegram_id
    }
    if not telegram_ids:
        return

    tournament = None
    game = db.session.get(Game, assignments[0]["game_id"])
    if game and game.tournament:
        tournament = game.tournament

    players_payload = [
        {
            "telegram_id": telegram_ids[a["player_id"]],
            "tournament_name": tournament.name if tournament else None,
            "round_number": a["round_number"],
            "table_number": a["table_number"],
            "seat_number": a["seat_number"],
        }
        for a in assignments
        if a["player_id"] in telegram_ids
    ]
    if not players_payload:
        return

    from app.services.bot_notify_service import BotNotifyService
    BotNotifyService.send_event("next-slot", {"players": players_payload})


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

GAMES_PER_PAGE = 12


@games_bp.route("/")
def list_games():
    from sqlalchemy import select
    from datetime import datetime as dt

    # Незавершённые игры — отдельно, простым списком сверху (их обычно 0-1,
    # это рабочий инструмент админа "доиграть/завершить", а не архив).
    pending_games = (
        db.session.query(Game)
        .filter(Game.is_finished == False)
        .order_by(Game.played_at.desc())
        .all()
    )

    # Доступные месяцы для фильтра — по датам завершённых игр.
    finished_dates = [
        d for (d,) in db.session.query(Game.played_at).filter(Game.is_finished == True).all()
    ]
    available_months = sorted({d.strftime("%Y-%m") for d in finished_dates}, reverse=True)

    month = request.args.get("month")
    query = db.session.query(Game).filter(Game.is_finished == True)
    if month:
        try:
            start = dt.strptime(month, "%Y-%m")
        except ValueError:
            start = None
        if start:
            end = dt(start.year + 1, 1, 1) if start.month == 12 else dt(start.year, start.month + 1, 1)
            query = query.filter(Game.played_at >= start, Game.played_at < end)
    query = query.order_by(Game.played_at.desc())

    page = request.args.get("page", 1, type=int)
    pagination = db.paginate(query, page=page, per_page=GAMES_PER_PAGE, error_out=False)
    finished_games = pagination.items

    all_shown_games = pending_games + finished_games
    slots_by_game = {
        g.id: sorted(g.slots, key=lambda s: s.seat_number) for g in all_shown_games
    }
    player_ids = {s.player_id for slots in slots_by_game.values() for s in slots}
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "games/list.html",
        pending_games=pending_games,
        finished_games=finished_games,
        pagination=pagination,
        slots_by_game=slots_by_game,
        equipped_bulk=equipped_bulk,
        available_months=available_months,
        current_month=month,
    )


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
            role_str = request.form.get(f"role_{seat}") or Role.CIVILIAN.value
            if not pid_str:
                errors.append(f"Место {seat}: игрок обязателен.")
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

    from app.services.bot_notify_service import BotNotifyService
    for slot in game.slots:
        won = (
            (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
            or (slot.is_city_side and game.win_side == WinSide.CITY)
        )
        BotNotifyService.notify_player(
            slot.player_id, "game-finished",
            {"won": won, "total_score": slot.total_score, "bonus_score": slot.bonus_score},
        )

    # Авторассадка: если это была последняя незавершённая игра своего
    # раунда данной стадии — сразу же генерируем следующий раунд. Только
    # для игр, реально созданных через generate_next_round/generate_games
    # (у них round_number проставлен) — обычные ручные/не турнирные игры
    # (round_number is None) этот механизм не трогает.
    if game.stage_id and game.round_number is not None:
        remaining = (
            db.session.query(Game)
            .filter(
                Game.stage_id == game.stage_id,
                Game.round_number == game.round_number,
                Game.is_finished == False,
            )
            .count()
        )
        if remaining == 0:
            from app.services.tournament_service import TournamentService
            next_round_result = TournamentService.generate_next_round(game.stage_id)
            if next_round_result.ok:
                flash(f"Раунд {game.round_number} завершён — {next_round_result.message}", "info")
                _notify_next_slot(next_round_result.data)
            # Отсутствие следующего раунда (например, стадия почти закончена,
            # участников не хватает) — не ошибка самого finish_game, поэтому
            # неудачу generate_next_round здесь не показываем как danger.

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
