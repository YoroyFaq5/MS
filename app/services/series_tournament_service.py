"""
SeriesTournamentService
========================
«Серийный турнир» — один большой турнир (Tournament), состоящий из
нескольких независимых игровых серий («вечеров»). Каждая серия — это
TournamentStage с независимой (не эксклюзивной, в отличие от элиминационной
турнирной сетки) активацией.

Сервис максимально переиспользует TournamentService/RatingService — здесь
нет собственной логики подсчёта очков и рейтинга, только CRUD для новых
сущностей (SeriesTournament/TournamentSeries) и агрегация уже готовых
per-stage рейтингов в общий лидерборд серийного турнира.

Игры создаются/завершаются через уже существующий /games/new flow
(games.py) — Game.stage_id указывает на тот же TournamentStage, что и у
обычных турниров, поэтому PostGameOrchestrator/PostTournamentOrchestrator
(ELO, экономика, достижения, fantasy) продолжают работать автоматически,
без единого изменения в orchestrator.py.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date as date_type
from typing import Dict, List, Optional

from sqlalchemy import func

from app import db
from app.models import (
    Tournament, TournamentType, StageType,
    SeriesTournament, TournamentSeries, SeriesStatus,
    Game, GameSlot,
)
from app.services.tournament_service import TournamentService

logger = logging.getLogger(__name__)


@dataclass
class SeriesResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "SeriesResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "SeriesResult":
        return cls(ok=False, message=msg)


@dataclass
class SeriesOverallEntry:
    """Строка общего лидерборда серийного турнира — сумма по всем
    (не отменённым) сериям, в которых участвовал игрок."""
    player_id: int
    display_name: str
    series_played: int = 0
    games_played: int = 0
    games_won: int = 0
    total_score: float = 0.0
    bonus_points: float = 0.0
    win_rate: float = 0.0
    avg_score_per_game: float = 0.0
    avg_score_per_series: float = 0.0
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "player_id": self.player_id,
            "display_name": self.display_name,
            "series_played": self.series_played,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "total_score": round(self.total_score, 2),
            "bonus_points": round(self.bonus_points, 2),
            "win_rate": round(self.win_rate, 1),
            "avg_score_per_game": round(self.avg_score_per_game, 2),
            "avg_score_per_series": round(self.avg_score_per_series, 2),
        }


class SeriesTournamentService:

    # ── Серийный турнир (обёртка над Tournament) ─────────────────────────────

    @staticmethod
    def create_series_tournament(
        name: str, description: str = "", is_ranked: bool = True,
    ) -> SeriesResult:
        """
        has_stages=False на этапе создания — иначе TournamentService
        автоматически создаст лишние этапы «Основной этап»/«Финал»
        (элиминационная механика, к сериям отношения не имеющая).
        Включаем has_stages постфактум, напрямую — это не запускает
        автосоздание этапов (оно происходит только внутри create_tournament).
        """
        result = TournamentService.create_tournament(
            name=name, t_type=TournamentType.INDIVIDUAL,
            is_ranked=is_ranked, has_stages=False, description=description,
        )
        if not result.ok:
            return SeriesResult.fail(result.message)

        tournament: Tournament = result.data
        tournament.has_stages = True
        st = SeriesTournament(tournament_id=tournament.id)
        db.session.add(st)
        db.session.commit()
        logger.info(f"Series tournament created: {tournament.name!r} (id={st.id})")
        return SeriesResult.success(f"Серийный турнир «{tournament.name}» создан.", data=st)

    @staticmethod
    def get_series_tournament(series_tournament_id: int) -> Optional[SeriesTournament]:
        return db.session.get(SeriesTournament, series_tournament_id)

    @staticmethod
    def list_series_tournaments() -> List[SeriesTournament]:
        return (
            db.session.query(SeriesTournament)
            .join(Tournament)
            .order_by(Tournament.created_at.desc())
            .all()
        )

    # ── Серии ──────────────────────────────────────────────────────────────────

    @staticmethod
    def add_series(
        series_tournament_id: int, name: str, series_date: Optional[date_type] = None,
    ) -> SeriesResult:
        st = db.session.get(SeriesTournament, series_tournament_id)
        if not st:
            return SeriesResult.fail("Серийный турнир не найден.")
        if not name or not name.strip():
            return SeriesResult.fail("Название серии обязательно.")

        stage_result = TournamentService.add_stage(
            st.tournament_id, name=name.strip(), stage_type=StageType.GROUP,
        )
        if not stage_result.ok:
            return SeriesResult.fail(stage_result.message)
        stage = stage_result.data

        # Серии активируются независимо друг от друга — в отличие от
        # элиминационных этапов, у серий нет правила «только одна активна
        # одновременно», поэтому TournamentService.activate_stage() здесь
        # намеренно не используется (у него ещё и требование
        # tournament.status == "active", которое серийным турнирам, живущим
        # в статусе "pending" весь свой жизненный цикл, не подходит).
        stage.status = "active"

        max_order = max((s.order for s in st.series), default=0)
        series = TournamentSeries(
            series_tournament_id=st.id,
            stage_id=stage.id,
            name=name.strip(),
            series_date=series_date,
            order=max_order + 1,
            status=SeriesStatus.ACTIVE,
        )
        db.session.add(series)
        db.session.commit()
        logger.info(f"Series added: {series.name!r} to series_tournament#{st.id}")
        return SeriesResult.success(f"Серия «{series.name}» добавлена.", data=series)

    @staticmethod
    def finish_series(series_id: int) -> SeriesResult:
        series = db.session.get(TournamentSeries, series_id)
        if not series:
            return SeriesResult.fail("Серия не найдена.")
        if series.status != SeriesStatus.ACTIVE:
            return SeriesResult.fail(
                f"Завершить можно только активную серию (сейчас: «{series.status.value}»)."
            )

        # Переиспользуем существующую валидацию TournamentService.finish_stage —
        # у неё, в отличие от activate_stage, нет ограничения "только один
        # активный этап", так что реюз здесь безопасен.
        stage_result = TournamentService.finish_stage(series.stage_id)
        if not stage_result.ok:
            return SeriesResult.fail(stage_result.message)

        series.status = SeriesStatus.FINISHED
        db.session.commit()

        # Fantasy-драфты, сделанные именно на эту серию — блокируем и сразу
        # считаем очки (переиспользуем ту же связку lock+score, что и у
        # турнирного Fantasy при старте/завершении турнира, см.
        # TournamentService.start_tournament/PostTournamentOrchestrator).
        try:
            from app.services.fantasy_service import FantasyService
            FantasyService.lock_drafts_for_series(series.id, commit=True)
            FantasyService.score_series(series.id, commit=True)
        except Exception:
            logger.exception(f"Failed to score fantasy drafts for series #{series.id}")

        return SeriesResult.success(f"Серия «{series.name}» завершена.", data=series)

    @staticmethod
    def cancel_series(series_id: int) -> SeriesResult:
        series = db.session.get(TournamentSeries, series_id)
        if not series:
            return SeriesResult.fail("Серия не найдена.")
        if series.status in (SeriesStatus.FINISHED, SeriesStatus.CANCELLED):
            return SeriesResult.fail(f"Нельзя отменить серию в статусе «{series.status.value}».")

        series.status = SeriesStatus.CANCELLED
        # Сразу блокируем приём новых игр в отменённую серию, переиспользуя
        # существующую проверку games.py ("этап должен быть активен") —
        # никаких изменений в games.py не требуется.
        if series.stage:
            series.stage.status = "finished"
        db.session.commit()
        logger.info(f"Series cancelled: {series.name!r} (id={series.id})")
        return SeriesResult.success(f"Серия «{series.name}» отменена.", data=series)

    # ── Лидерборды ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_series_leaderboard(series_id: int):
        """Лидерборд одной серии — чистый passthrough к
        RatingService.get_stage_rating(), без новой логики подсчёта."""
        from app.services.rating_service import RatingService

        series = db.session.get(TournamentSeries, series_id)
        if not series:
            return []
        return RatingService.get_stage_rating(series.stage_id)

    @staticmethod
    def get_overall_leaderboard(series_tournament_id: int) -> List[SeriesOverallEntry]:
        """
        Общий рейтинг по всем НЕ отменённым сериям турнира. Суммирует уже
        готовые per-stage рейтинги (RatingService.get_stage_rating) — не
        пересчитывает очки/победы заново. bonus_points — единственная
        действительно новая цифра: один агрегирующий запрос по уже
        существующей колонке GameSlot.bonus_score, без переопределения
        формулы рейтинга.

        Tie-break: total_score → win_rate → series_played → bonus_points
        (все по убыванию).
        """
        from app.services.rating_service import RatingService

        st = db.session.get(SeriesTournament, series_tournament_id)
        if not st:
            return []

        active_series = [s for s in st.series if s.status != SeriesStatus.CANCELLED]
        if not active_series:
            return []

        agg: Dict[int, SeriesOverallEntry] = {}
        for series in active_series:
            ratings = RatingService.get_stage_rating(series.stage_id)
            if not ratings:
                continue  # пустая серия — не влияет на итоговый рейтинг
            for r in ratings:
                e = agg.setdefault(
                    r.player_id,
                    SeriesOverallEntry(player_id=r.player_id, display_name=r.display_name),
                )
                e.series_played += 1
                e.games_played += r.games_played
                e.games_won += r.games_won
                e.total_score += r.total_score

        if not agg:
            return []

        bonus_rows = (
            db.session.query(GameSlot.player_id, func.sum(GameSlot.bonus_score))
            .join(Game)
            .filter(Game.tournament_id == st.tournament_id, Game.is_finished == True)
            .group_by(GameSlot.player_id)
            .all()
        )
        for player_id, bonus_sum in bonus_rows:
            if player_id in agg:
                agg[player_id].bonus_points = round(bonus_sum or 0.0, 2)

        entries = list(agg.values())
        for e in entries:
            e.win_rate = round(e.games_won / e.games_played * 100, 1) if e.games_played else 0.0
            e.avg_score_per_game = round(e.total_score / e.games_played, 2) if e.games_played else 0.0
            e.avg_score_per_series = round(e.total_score / e.series_played, 2) if e.series_played else 0.0
            e.total_score = round(e.total_score, 2)

        entries.sort(key=lambda e: (-e.total_score, -e.win_rate, -e.series_played, -e.bonus_points))
        for i, e in enumerate(entries, 1):
            e.rank = i
        return entries

    @staticmethod
    def get_player_series_breakdown(series_tournament_id: int, player_id: int) -> List[dict]:
        """
        Построчно по каждой не отменённой серии — результат конкретного
        игрока (entry=None, если он в этой серии не участвовал — игрок
        мог сыграть не все серии турнира).
        """
        from app.services.rating_service import RatingService

        st = db.session.get(SeriesTournament, series_tournament_id)
        if not st:
            return []

        breakdown = []
        for series in sorted(st.series, key=lambda s: s.order):
            if series.status == SeriesStatus.CANCELLED:
                continue
            ratings = RatingService.get_stage_rating(series.stage_id)
            entry = next((r for r in ratings if r.player_id == player_id), None)
            breakdown.append({"series": series, "entry": entry})
        return breakdown
