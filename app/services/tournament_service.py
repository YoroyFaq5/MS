"""
TournamentService
=================
All tournament domain logic. No Flask imports. No views logic.

Responsibilities:
  - Tournament lifecycle (create → activate → finish)
  - Stage management (advance, cutoff, activate final)
  - Participant/team registration
  - Cutoff computation (top-N by stage rating → advance to final)
  - Anti-abuse validation
  - Game ↔ Tournament linkage helpers
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from app import db
from app.models import (
    Tournament, TournamentStage, TournamentParticipant,
    Team, TeamPlayer, Game, Player,
    TournamentType, StageType, WinSide,
)
from app.services.rating_service import RatingService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Result / Error types (no exceptions as control flow in views)
# ---------------------------------------------------------------------------

@dataclass
class ServiceResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "ServiceResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "ServiceResult":
        return cls(ok=False, message=msg)


# ---------------------------------------------------------------------------
# Tournament lifecycle
# ---------------------------------------------------------------------------

class TournamentService:

    # ── Create ───────────────────────────────────────────────────────────────

    @staticmethod
    def create_tournament(
        name: str,
        t_type: TournamentType = TournamentType.INDIVIDUAL,
        is_ranked: bool = True,
        has_stages: bool = False,
        cutoff_size: int = 10,
        description: str = "",
    ) -> ServiceResult:
        """Create a new tournament in 'pending' status."""
        if not name or not name.strip():
            return ServiceResult.fail("Название турнира обязательно.")

        existing = db.session.query(Tournament).filter_by(name=name.strip()).first()
        if existing:
            return ServiceResult.fail(f"Турнир «{name}» уже существует.")

        t = Tournament(
            name=name.strip(),
            description=description.strip() or None,
            type=t_type,
            is_ranked=is_ranked,
            has_stages=has_stages,
            cutoff_size=max(2, min(cutoff_size, 100)),
            status="pending",
        )
        db.session.add(t)
        db.session.flush()

        # Auto-create stages if requested
        if has_stages:
            TournamentService._auto_create_stages(t)

        db.session.commit()
        logger.info(f"Tournament created: {t!r}")
        return ServiceResult.success(f"Турнир «{t.name}» создан.", data=t)

    @staticmethod
    def _auto_create_stages(tournament: Tournament) -> None:
        """Create default Main + Final stages."""
        main = TournamentStage(
            tournament_id=tournament.id,
            name="Основной этап",
            order=1,
            type=StageType.MAIN,
            status="pending",
        )
        final = TournamentStage(
            tournament_id=tournament.id,
            name="Финал",
            order=2,
            type=StageType.FINAL,
            status="pending",
        )
        db.session.add_all([main, final])

    # ── Status transitions ────────────────────────────────────────────────────

    @staticmethod
    def activate_tournament(tournament_id: int) -> ServiceResult:
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if t.status != "pending":
            return ServiceResult.fail(f"Турнир уже в статусе «{t.status}».")

        participant_count = len(t.participants)
        if participant_count < 2:
            return ServiceResult.fail("Нужно минимум 2 участника для старта.")

        t.status = "active"
        t.started_at = datetime.now(timezone.utc)

        # Activate first stage if stages exist
        if t.has_stages and t.stages:
            first_stage = sorted(t.stages, key=lambda s: s.order)[0]
            first_stage.status = "active"

        db.session.commit()

        # Fantasy picks must freeze once the tournament actually starts —
        # otherwise users could keep editing drafts while results are
        # already known. (Bug: this used to only happen at tournament
        # finish, so drafts stayed editable for the whole active phase.)
        try:
            from app.services.fantasy_service import FantasyService
            FantasyService.lock_drafts_for_tournament(tournament_id, commit=True)
        except Exception:
            logger.exception(f"Failed to lock fantasy drafts for tournament #{tournament_id}")

        return ServiceResult.success(f"Турнир «{t.name}» запущен.", data=t)

    @staticmethod
    def finish_tournament(tournament_id: int) -> ServiceResult:
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if t.status == "finished":
            return ServiceResult.fail("Турнир уже завершён.")

        t.status = "finished"
        t.finished_at = datetime.now(timezone.utc)

        # Close all active stages
        for stage in t.stages:
            if stage.status == "active":
                stage.status = "finished"

        db.session.commit()
        return ServiceResult.success(f"Турнир «{t.name}» завершён.", data=t)

    # ── Participants ──────────────────────────────────────────────────────────

    @staticmethod
    def register_participant(tournament_id: int, player_id: int) -> ServiceResult:
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if t.status == "finished":
            return ServiceResult.fail("Нельзя регистрировать в завершённый турнир.")

        player = db.session.get(Player, player_id)
        if not player or not player.is_active:
            return ServiceResult.fail("Игрок не найден или неактивен.")

        exists = db.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament_id, player_id=player_id
        ).first()
        if exists:
            return ServiceResult.fail(f"«{player.display_name}» уже участвует в этом турнире.")

        p = TournamentParticipant(
            tournament_id=tournament_id,
            player_id=player_id,
        )
        db.session.add(p)
        db.session.commit()
        return ServiceResult.success(f"«{player.display_name}» зарегистрирован.", data=p)

    @staticmethod
    def remove_participant(tournament_id: int, player_id: int) -> ServiceResult:
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if t.status == "active":
            return ServiceResult.fail("Нельзя удалить участника из активного турнира.")

        p = db.session.query(TournamentParticipant).filter_by(
            tournament_id=tournament_id, player_id=player_id
        ).first()
        if not p:
            return ServiceResult.fail("Участник не найден.")

        db.session.delete(p)
        db.session.commit()
        return ServiceResult.success("Участник удалён.")

    # ── Teams ─────────────────────────────────────────────────────────────────

    @staticmethod
    def create_team(tournament_id: int, name: str, color: Optional[str] = None) -> ServiceResult:
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if t.type != TournamentType.TEAM:
            return ServiceResult.fail("Этот турнир не командный.")
        if not name.strip():
            return ServiceResult.fail("Название команды обязательно.")

        exists = db.session.query(Team).filter_by(
            tournament_id=tournament_id, name=name.strip()
        ).first()
        if exists:
            return ServiceResult.fail(f"Команда «{name}» уже существует.")

        team = Team(tournament_id=tournament_id, name=name.strip(), color=color)
        db.session.add(team)
        db.session.commit()
        return ServiceResult.success(f"Команда «{team.name}» создана.", data=team)

    @staticmethod
    def add_player_to_team(team_id: int, player_id: int) -> ServiceResult:
        team = db.session.get(Team, team_id)
        if not team:
            return ServiceResult.fail("Команда не найдена.")

        player = db.session.get(Player, player_id)
        if not player:
            return ServiceResult.fail("Игрок не найден.")

        # Anti-abuse: one team per tournament per player
        conflict = (
            db.session.query(TeamPlayer)
            .join(Team)
            .filter(
                Team.tournament_id == team.tournament_id,
                TeamPlayer.player_id == player_id,
            )
            .first()
        )
        if conflict:
            return ServiceResult.fail(
                f"«{player.display_name}» уже в другой команде этого турнира."
            )

        # Also register as tournament participant if not already
        part_exists = db.session.query(TournamentParticipant).filter_by(
            tournament_id=team.tournament_id, player_id=player_id
        ).first()
        if not part_exists:
            p = TournamentParticipant(
                tournament_id=team.tournament_id,
                player_id=player_id,
                team_id=team_id,
            )
            db.session.add(p)
        else:
            part_exists.team_id = team_id

        tp = TeamPlayer(team_id=team_id, player_id=player_id)
        db.session.add(tp)
        db.session.commit()
        return ServiceResult.success(f"«{player.display_name}» добавлен в команду «{team.name}».", data=tp)

    # ── Stages & Cutoff ───────────────────────────────────────────────────────

    @staticmethod
    def add_stage(
        tournament_id: int,
        name: str,
        stage_type: StageType = StageType.MAIN,
        order: Optional[int] = None,
    ) -> ServiceResult:
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if not t.has_stages:
            return ServiceResult.fail("У этого турнира нет этапов (has_stages=False).")
        if t.status == "finished":
            return ServiceResult.fail("Нельзя добавлять этапы в завершённый турнир.")

        if order is None:
            max_order = max((s.order for s in t.stages), default=0)
            order = max_order + 1

        stage = TournamentStage(
            tournament_id=tournament_id,
            name=name.strip(),
            order=order,
            type=stage_type,
            status="pending",
        )
        db.session.add(stage)
        db.session.commit()
        return ServiceResult.success(f"Этап «{name}» добавлен.", data=stage)

    @staticmethod
    def activate_stage(stage_id: int) -> ServiceResult:
        stage = db.session.get(TournamentStage, stage_id)
        if not stage:
            return ServiceResult.fail("Этап не найден.")
        if stage.status != "pending":
            return ServiceResult.fail(f"Этап уже в статусе «{stage.status}».")

        tournament = stage.tournament
        if tournament.status != "active":
            return ServiceResult.fail("Турнир должен быть в статусе 'active'.")

        # Only one stage active at a time (sequential model)
        active_stage = tournament.active_stage
        if active_stage and active_stage.id != stage_id:
            return ServiceResult.fail(
                f"Уже активен этап «{active_stage.name}». Сначала завершите его."
            )

        stage.status = "active"
        db.session.commit()
        return ServiceResult.success(f"Этап «{stage.name}» активирован.", data=stage)

    @staticmethod
    def finish_stage(stage_id: int) -> ServiceResult:
        stage = db.session.get(TournamentStage, stage_id)
        if not stage:
            return ServiceResult.fail("Этап не найден.")
        if stage.status != "active":
            return ServiceResult.fail("Можно завершить только активный этап.")

        stage.status = "finished"
        db.session.commit()
        return ServiceResult.success(f"Этап «{stage.name}» завершён.", data=stage)

    @staticmethod
    def run_cutoff(stage_id: int) -> ServiceResult:
        """
        Cutoff algorithm:
        1. Compute stage rating for the given stage.
        2. Take top-N (tournament.cutoff_size) players.
        3. Mark their TournamentParticipant.advanced_to_final = True.
        4. Find the FINAL stage and activate it.
        5. Return the list of advancing players.

        Idempotent: safe to call multiple times.
        """
        stage = db.session.get(TournamentStage, stage_id)
        if not stage:
            return ServiceResult.fail("Этап не найден.")

        tournament = stage.tournament
        if stage.type == StageType.FINAL:
            return ServiceResult.fail("Нельзя применить cutoff к финальному этапу.")

        # Get rating for this stage
        stage_ratings = RatingService.get_stage_rating(stage_id)
        if not stage_ratings:
            return ServiceResult.fail("Нет данных для расчёта cutoff.")

        cutoff_n = tournament.cutoff_size
        advancing_ratings = stage_ratings[:cutoff_n]
        advancing_player_ids = {r.player_id for r in advancing_ratings}

        # Update participant records
        for part in tournament.participants:
            part.advanced_to_final = part.player_id in advancing_player_ids

        # Find final stage
        final_stage = next(
            (s for s in sorted(tournament.stages, key=lambda x: x.order)
             if s.type == StageType.FINAL),
            None,
        )
        if final_stage and final_stage.status == "pending":
            final_stage.status = "active"

        db.session.commit()
        logger.info(
            f"Cutoff applied for stage {stage_id}: "
            f"{len(advancing_player_ids)} players advance."
        )
        return ServiceResult.success(
            f"Cutoff выполнен. В финал проходят {len(advancing_player_ids)} игроков.",
            data={
                "advancing": [r.to_dict() for r in advancing_ratings],
                "final_stage": final_stage.to_dict() if final_stage else None,
            },
        )

    # ── Game linkage ──────────────────────────────────────────────────────────

    @staticmethod
    def link_game_to_tournament(
        game: Game,
        tournament_id: int,
        stage_id: Optional[int] = None,
    ) -> ServiceResult:
        """
        Attach an existing (unfinished) Game to a tournament/stage.
        Inherits is_ranked from tournament.
        """
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if t.status == "finished":
            return ServiceResult.fail("Нельзя привязать игру к завершённому турниру.")

        if stage_id:
            stage = db.session.get(TournamentStage, stage_id)
            if not stage or stage.tournament_id != tournament_id:
                return ServiceResult.fail("Этап не принадлежит этому турниру.")
            if stage.status != "active":
                return ServiceResult.fail("Этап не активен.")
            game.stage_id = stage_id

        game.tournament_id = tournament_id
        game.is_ranked = t.is_ranked
        db.session.commit()
        return ServiceResult.success("Игра привязана к турниру.", data=game)

    # ── Anti-abuse helpers ────────────────────────────────────────────────────

    @staticmethod
    def validate_game_participants(game: Game, tournament_id: int) -> ServiceResult:
        """
        Ensure all players in a game are registered participants
        of the given tournament. Call before finishing a tournament game.
        """
        participant_ids = {
            p.player_id
            for p in db.session.query(TournamentParticipant)
            .filter_by(tournament_id=tournament_id)
            .all()
        }
        for slot in game.slots:
            if slot.player_id not in participant_ids:
                player = db.session.get(Player, slot.player_id)
                name = player.display_name if player else str(slot.player_id)
                return ServiceResult.fail(
                    f"«{name}» не является участником турнира."
                )
        return ServiceResult.success("Все участники валидны.")

    @staticmethod
    def get_final_stage_participants(tournament_id: int) -> List[TournamentParticipant]:
        """Return participants who advanced to the final stage."""
        return (
            db.session.query(TournamentParticipant)
            .filter_by(tournament_id=tournament_id, advanced_to_final=True)
            .all()
        )

    # ── Bulk game generation ────────────────────────────────────────────────────

    @staticmethod
    def generate_games(
        tournament_id: int,
        n_games: int,
        stage_id: Optional[int] = None,
    ) -> ServiceResult:
        """
        Generate n_games empty Game shells for a tournament, assigning
        participants to seats using a rotation schedule that maximises seat
        diversity — each player sits in each seat as rarely as possible —
        AND balances the total number of games each participant plays
        (differs by at most 1 across the whole tournament, not just this
        batch — see games_played_count below).

        Algorithm:
        - WHO plays in a given game: greedy — always pick the GAME_SIZE
          participants with the fewest games played so far (ties broken by
          participant order). This is the standard fair-scheduling
          guarantee: after any number of games, max(count) - min(count) <= 1.
        - WHICH SEAT each of them sits in: unchanged — greedy seat
          assignment scored by historical seat usage.
        - Both counters are seeded from games that already exist in this
          tournament (not just this batch), so fairness holds across
          repeated calls to generate_games on the same tournament, not only
          within a single call.

        Roles are pre-filled with the default distribution (6 civ / 2 mafia /
        1 don / 1 sheriff) so the admin only needs to fill in results.
        """
        from app.models import Game, GameSlot, WinSide, Role, TournamentParticipant  # Role.CIVILIAN placeholder
        from collections import Counter, defaultdict

        t = db.session.get(Tournament, tournament_id)
        if not t:
            return ServiceResult.fail("Турнир не найден.")
        if t.status == "finished":
            return ServiceResult.fail("Нельзя добавлять игры в завершённый турнир.")
        if not (1 <= n_games <= 200):
            return ServiceResult.fail("Количество игр: от 1 до 200.")

        if stage_id:
            stage = db.session.get(TournamentStage, stage_id)
            if not stage or stage.tournament_id != tournament_id:
                return ServiceResult.fail("Этап не принадлежит этому турниру.")

        participant_ids = [
            p.player_id for p in
            db.session.query(TournamentParticipant)
            .filter_by(tournament_id=tournament_id).all()
        ]
        if len(participant_ids) < 10:
            return ServiceResult.fail(
                f"Нужно минимум 10 участников. Сейчас: {len(participant_ids)}."
            )

        GAME_SIZE = 10
        pool = participant_ids[:]

        # seat_usage[player_id][seat_number] → count of times used
        # games_played_count[player_id] → total games in this tournament
        # Seeded from games already in the tournament (manually created or
        # from a previous generate_games call) so fairness is tournament-wide,
        # not reset to zero on every call.
        seat_usage: dict[int, Counter] = defaultdict(Counter)
        games_played_count: dict[int, int] = defaultdict(int)
        existing_slots = (
            db.session.query(GameSlot)
            .join(Game)
            .filter(Game.tournament_id == tournament_id, GameSlot.player_id.in_(pool))
            .all()
        )
        for slot in existing_slots:
            seat_usage[slot.player_id][slot.seat_number] += 1
            games_played_count[slot.player_id] += 1

        created_ids = []

        for game_idx in range(n_games):
            # Кто играет в этой игре: жадно берём GAME_SIZE участников с
            # наименьшим текущим числом сыгранных игр — гарантирует разброс
            # не больше 1 между любыми двумя участниками в конце генерации,
            # для любого сочетания числа участников/игр (в отличие от
            # прежнего фиксированного окна, которое было честным только в
            # частных случаях).
            candidates = sorted(pool, key=lambda pid: (games_played_count[pid], pid))
            players_this_game = candidates[:GAME_SIZE]

            # Greedy seat assignment: for each seat pick the player who has
            # sat there least often (ties broken by total games played)
            remaining = list(players_this_game)
            assigned: dict[int, int] = {}  # seat → player_id

            for seat in range(1, GAME_SIZE + 1):
                remaining.sort(key=lambda pid: (seat_usage[pid][seat], sum(seat_usage[pid].values())))
                chosen = remaining.pop(0)
                assigned[seat] = chosen
                seat_usage[chosen][seat] += 1
                games_played_count[chosen] += 1

            game = Game(
                win_side=WinSide.NONE,
                is_finished=False,
                is_ranked=t.is_ranked,
                tournament_id=tournament_id,
                stage_id=stage_id,
                notes=f"Игра {game_idx + 1}/{n_games}",
            )
            db.session.add(game)
            db.session.flush()

            for seat_num, player_id in assigned.items():
                db.session.add(GameSlot(
                    game_id=game.id,
                    player_id=player_id,
                    seat_number=seat_num,
                    role=Role.CIVILIAN,   # placeholder — admin assigns roles when finishing
                    base_score=0.0,
                    bonus_score=0.0,
                ))
            created_ids.append(game.id)

        db.session.commit()
        return ServiceResult.success(
            f"Создано {n_games} игр для турнира «{t.name}».",
            data={"game_ids": created_ids, "count": len(created_ids)},
        )

    # ── Авторассадка следующего раунда (правила клуба) ──────────────────────────
    # (1) минимизировать попадание игрока на тот же слот, где он уже сидел
    #     (в рамках турнира); (2) минимизировать повторение состава стола,
    #     если играющих в раунде ≥ 20 (при одном столе выбора состава нет);
    # (3) если участников не кратно 10 — remainder игроков отдыхают этот
    #     раунд, ротация честная (в т.ч. общий случай для турнира "Стол
    #     года" с 11 участниками — не частный случай, а remainder=1).

    @staticmethod
    def _group_into_tables(player_ids: list[int], n_tables: int, pairing_count) -> list[list[int]]:
        """
        Разбивка играющих на n_tables столов по 10, минимизируя суммарное
        число повторных пар (кто уже играл с кем вместе в этом турнире).
        NP-трудная в общем виде задача («social golfer problem») — практичная
        эвристика: случайная стартовая раскладка + локальный поиск (пробуем
        поменять местами двух игроков из разных столов, оставляем обмен,
        только если он уменьшает суммарный счёт повторов).
        """
        import random

        shuffled = list(player_ids)
        random.shuffle(shuffled)
        tables = [shuffled[i * 10:(i + 1) * 10] for i in range(n_tables)]

        def total_cost() -> int:
            cost = 0
            for table in tables:
                for i in range(len(table)):
                    for j in range(i + 1, len(table)):
                        cost += pairing_count[frozenset((table[i], table[j]))]
            return cost

        best_cost = total_cost()
        for _ in range(500):
            if best_cost == 0:
                break
            ta, tb = random.sample(range(n_tables), 2)
            ia, ib = random.randrange(10), random.randrange(10)
            tables[ta][ia], tables[tb][ib] = tables[tb][ib], tables[ta][ia]
            new_cost = total_cost()
            if new_cost < best_cost:
                best_cost = new_cost
            else:
                tables[ta][ia], tables[tb][ib] = tables[tb][ib], tables[ta][ia]
        return tables

    @staticmethod
    def generate_next_round(stage_id: int) -> ServiceResult:
        """
        Создаёт игры следующего раунда стадии турнира с рассадкой по
        правилам клуба (см. блок выше). История пар/мест считается на лету
        по уже существующим слотам этого ТУРНИРА (не всей карьеры игрока,
        не только этой стадии) — включая ещё не сыгранные, ранее
        сгенерированные раунды. Идемпотентно в том смысле, что каждый
        вызов создаёт СЛЕДУЮЩИЙ раунд (по max(round_number) в стадии) —
        повторный вызов без завершения текущего раунда просто создаст ещё
        один раунд поверх, ничего не перезаписывая.
        """
        from app.models import GameSlot, Role
        from collections import Counter, defaultdict
        from sqlalchemy import func

        stage = db.session.get(TournamentStage, stage_id)
        if not stage:
            return ServiceResult.fail("Этап не найден.")
        tournament = stage.tournament
        if stage.status != "active":
            return ServiceResult.fail(f"Этап «{stage.name}» не активен.")

        if stage.type == StageType.FINAL:
            eligible_ids = [p.player_id for p in tournament.participants if p.advanced_to_final]
        else:
            eligible_ids = [p.player_id for p in tournament.participants]

        if len(eligible_ids) < 10:
            return ServiceResult.fail(
                f"Недостаточно участников для раунда: {len(eligible_ids)} (нужно ≥10)."
            )

        current_round = (
            db.session.query(func.max(Game.round_number))
            .filter(Game.stage_id == stage_id, Game.round_number.isnot(None))
            .scalar()
        ) or 0
        next_round = current_round + 1

        existing_slots = (
            db.session.query(GameSlot.player_id, GameSlot.seat_number, GameSlot.game_id)
            .join(Game)
            .filter(Game.tournament_id == tournament.id)
            .all()
        )
        seat_usage: dict[int, Counter] = defaultdict(Counter)
        games_played_count: dict[int, int] = defaultdict(int)
        slots_by_game: dict[int, list[int]] = defaultdict(list)
        for player_id, seat_number, game_id in existing_slots:
            seat_usage[player_id][seat_number] += 1
            games_played_count[player_id] += 1
            slots_by_game[game_id].append(player_id)

        pairing_count: Counter = Counter()
        for players_in_game in slots_by_game.values():
            for i in range(len(players_in_game)):
                for j in range(i + 1, len(players_in_game)):
                    pairing_count[frozenset((players_in_game[i], players_in_game[j]))] += 1

        # Кто отдыхает этот раунд, если участников не кратно 10 — отдыхают
        # те, кто уже сыграл БОЛЬШЕ всех (честная ротация, зеркально
        # generate_games, который отдаёт приоритет играющим МЕНЬШЕ всех).
        remainder = len(eligible_ids) % 10
        resting_ids: list[int] = []
        if remainder:
            resting_ids = sorted(
                eligible_ids, key=lambda pid: (-games_played_count[pid], pid)
            )[:remainder]
        playing_ids = [pid for pid in eligible_ids if pid not in resting_ids]

        n_tables = len(playing_ids) // 10
        if n_tables == 0:
            return ServiceResult.fail("Недостаточно играющих для стола после ротации отдыха.")

        tables = (
            [list(playing_ids)] if n_tables == 1
            else TournamentService._group_into_tables(playing_ids, n_tables, pairing_count)
        )

        created_games = []
        assignments = []  # для будущего уведомления бота (см. MS-TelegramBot)
        for table_idx, table_players in enumerate(tables, start=1):
            remaining = list(table_players)
            seat_assignment: dict[int, int] = {}
            for seat in range(1, 11):
                remaining.sort(key=lambda pid: (seat_usage[pid][seat], sum(seat_usage[pid].values())))
                chosen = remaining.pop(0)
                seat_assignment[seat] = chosen
                seat_usage[chosen][seat] += 1

            game = Game(
                win_side=WinSide.NONE,
                is_finished=False,
                is_ranked=tournament.is_ranked,
                tournament_id=tournament.id,
                stage_id=stage_id,
                round_number=next_round,
                notes=f"Раунд {next_round}, стол {table_idx}",
            )
            db.session.add(game)
            db.session.flush()

            for seat_num, player_id in seat_assignment.items():
                db.session.add(GameSlot(
                    game_id=game.id, player_id=player_id,
                    seat_number=seat_num, role=Role.CIVILIAN,
                    base_score=0.0, bonus_score=0.0,
                ))
                assignments.append({
                    "player_id": player_id, "game_id": game.id,
                    "table_number": table_idx, "seat_number": seat_num,
                    "round_number": next_round,
                })
            created_games.append(game.id)

        db.session.commit()
        logger.info(
            f"Раунд {next_round} стадии {stage_id}: создано {len(created_games)} игр, "
            f"отдыхают {len(resting_ids)} игроков."
        )
        return ServiceResult.success(
            f"Раунд {next_round} создан: {len(created_games)} стол(ов)"
            + (f", отдыхают {len(resting_ids)} игроков" if resting_ids else "") + ".",
            data={
                "round_number": next_round,
                "game_ids": created_games,
                "resting_player_ids": resting_ids,
                "assignments": assignments,
            },
        )

    # ── Summary / context builders ────────────────────────────────────────────

    @staticmethod
    def get_tournament_summary(tournament_id: int) -> Optional[dict]:
        """
        Build full tournament context dict for templates / API.
        Avoids business logic in views.
        """
        t = db.session.get(Tournament, tournament_id)
        if not t:
            return None

        stages_data = [s.to_dict() for s in sorted(t.stages, key=lambda s: s.order)]
        games_finished = sum(1 for g in t.games if g.is_finished)
        games_total = len(t.games)

        player_ratings = RatingService.get_tournament_rating(tournament_id)
        team_ratings = (
            RatingService.get_team_rating(tournament_id)
            if t.type == TournamentType.TEAM
            else []
        )

        return {
            "tournament": t,
            "stages": stages_data,
            "games_finished": games_finished,
            "games_total": games_total,
            "participant_count": len(t.participants),
            "player_ratings": player_ratings,
            "team_ratings": team_ratings,
            "active_stage": t.active_stage,
        }
