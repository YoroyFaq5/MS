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
