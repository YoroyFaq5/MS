"""
PostGameOrchestrator / PostTournamentOrchestrator
=================================================
Event-driven orchestration layer.

These are the single entry points that chain service calls in the correct
order after key domain events. Views call one method; the orchestrator
coordinates RatingService → EconomyService → FantasyService → SeasonService.

This is the 'event handler' in an event-driven architecture.
In a full SaaS system these would be Celery tasks / background jobs.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from app import db
from app.models import Game, Tournament

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    ok: bool
    steps: List[str]
    errors: List[str]

    @classmethod
    def empty(cls) -> "OrchestratorResult":
        return cls(ok=True, steps=[], errors=[])

    def add_step(self, msg: str) -> None:
        self.steps.append(msg)
        logger.info(f"[Orchestrator] {msg}")

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.ok = False
        logger.error(f"[Orchestrator] ERROR: {msg}")


def _update_fantasy_live_points(tournament_id: Optional[int], stage_id: Optional[int]) -> None:
    """
    Recompute Fantasy draft total_points from the current rating right
    after a game is scored — otherwise standings sat at 0 the whole
    evening/tournament until it was explicitly finished and
    score_series()/score_tournament() ran, even though the underlying
    games were already finished. Does not touch draft.status or pay out
    the prize pool — that stays a deliberate one-time action tied to
    actually finishing the series/tournament.
    """
    if not tournament_id:
        return
    from app.services.fantasy_service import FantasyService
    FantasyService.update_live_points_for_tournament(tournament_id, commit=False)
    if stage_id:
        from app.models import TournamentSeries
        series = db.session.query(TournamentSeries).filter_by(stage_id=stage_id).first()
        if series:
            FantasyService.update_live_points_for_series(series.id, commit=False)


class PostGameOrchestrator:
    """
    Called immediately after a game is finished.
    Order: base scores → ELO → season assignment → coin rewards.
    """

    @staticmethod
    def run(game: Game) -> OrchestratorResult:
        from app.services.rating_service import RatingService
        from app.services.economy_service import EconomyService
        from app.services.season_service import SeasonService

        result = OrchestratorResult.empty()

        try:
            # 1. Base scores
            RatingService.apply_base_scores_to_game(game)
            result.add_step(f"Base scores applied to game #{game.id}")
        except Exception as e:
            result.add_error(f"Base scores failed: {e}")

        try:
            # 2. ELO update via new EloEngine (formula: Δμᵢ = α(Rᵢ-Eᵢ)kᵢuᵢ + αsᵢK + λbᵢ)
            if game.is_ranked:
                from app.services.elo_engine import EloEngine
                deltas = EloEngine.apply_match(game, commit=False)
                result.add_step(
                    f"ELO updated via EloEngine: {len(deltas)} deltas applied"
                )
        except Exception as e:
            result.add_error(f"ELO update failed: {e}")

        try:
            # 3. Season assignment (idempotent)
            season = SeasonService.resolve_season_for_game(game)
            if season:
                result.add_step(f"Game assigned to season: {season.name}")
        except Exception as e:
            result.add_error(f"Season assignment failed: {e}")

        try:
            # 3b. Компенсационные баллы ФСМ (п.8.6.1-8.6.5) — только для
            # игр внутри турнира, дистанция = весь турнир целиком.
            if game.tournament_id:
                RatingService.recompute_compensation_points(
                    game.tournament_id, commit=False,
                )
                result.add_step("Compensation points recomputed")
        except Exception as e:
            result.add_error(f"Compensation points failed: {e}")

        try:
            # 3c. Fantasy live points (превью, не финальный подсчёт)
            _update_fantasy_live_points(game.tournament_id, game.stage_id)
            result.add_step("Fantasy live points updated")
        except Exception as e:
            result.add_error(f"Fantasy live points failed: {e}")

        try:
            # 4. Coin rewards — as_of=game.played_at делает дневной анти-абьюз
            # кап привязанным к реальной дате игры, а не моменту вызова.
            # Для обычных (только что сыгранных) игр played_at и "сейчас"
            # совпадают с точностью до секунд — поведение не меняется.
            # Это то, что позволяет Migration API (см. migration_service.py)
            # корректно реплеить исторические игры без ложного упора в кап.
            rewards = EconomyService.apply_rewards_after_game(
                game, commit=False, as_of=game.played_at,
            )
            ok_count = sum(1 for r in rewards if r.ok)
            result.add_step(f"Coins distributed: {ok_count} players rewarded")
        except Exception as e:
            result.add_error(f"Coin rewards failed: {e}")

        try:
            db.session.commit()
            result.add_step("Committed all changes")
        except Exception as e:
            db.session.rollback()
            result.add_error(f"Commit failed: {e}")

        try:
            # 5. Achievement checks (after everything above is persisted)
            from app.services.achievement_service import AchievementService
            unlocked = AchievementService.check_after_game(game)
            newly = sum(1 for r in unlocked if r.ok and r.data)
            result.add_step(f"Achievements checked: {newly} unlocked")
        except Exception as e:
            result.add_error(f"Achievement check failed: {e}")

        return result


class EditGameOrchestrator:
    """
    Called after an admin edits an already-finished game (roles, win side,
    bonus/PU, or which player occupies a seat). Unlike PostGameOrchestrator,
    this must first UNDO the game's old side effects before reapplying the
    corrected ones:

    - ELO is a running total, not reversible per-game in isolation — see
      EloEngine.recompute_chain_from() for why this replays every ranked
      game from this one onward instead of just recomputing this one game.
    - Economy (coins) IS precisely reversible per-game (CoinTransaction.
      ref_game_id) — reverse the old reward, then reapply the new one.
    - Achievements have no per-game reference in the data model at all
      (PlayerAchievement has no ref_game_id), so an incorrectly-granted
      achievement from the old (wrong) result can't be reliably revoked —
      out of scope. check_after_game() is still re-run so any newly
      correct achievement gets granted (idempotent, additive-only).
    - Season assignment is per-game/per-date, not cumulative — safe to
      just re-run for this one game like PostGameOrchestrator does.
    """

    @staticmethod
    def run(
        game: Game,
        old_player_ids: List[int],
        old_tournament_id: Optional[int] = None,
        old_stage_id: Optional[int] = None,
    ) -> "OrchestratorResult":
        from app.services.rating_service import RatingService
        from app.services.economy_service import EconomyService
        from app.services.season_service import SeasonService
        from app.services.elo_engine import EloEngine

        result = OrchestratorResult.empty()

        try:
            RatingService.apply_base_scores_to_game(game)
            result.add_step(f"Base scores recomputed for game #{game.id}")
        except Exception as e:
            result.add_error(f"Base scores failed: {e}")

        try:
            reversed_count = EconomyService.reverse_game_rewards(game, commit=False)
            db.session.flush()
            result.add_step(f"Reversed old rewards for {reversed_count} players")
        except Exception as e:
            result.add_error(f"Reward reversal failed: {e}")

        try:
            if game.is_ranked:
                replayed = EloEngine.recompute_chain_from(
                    game, extra_player_ids=old_player_ids, commit=False,
                )
                result.add_step(f"ELO chain recomputed: {replayed} games replayed")
        except Exception as e:
            result.add_error(f"ELO recompute failed: {e}")

        try:
            season = SeasonService.resolve_season_for_game(game)
            if season:
                result.add_step(f"Game assigned to season: {season.name}")
        except Exception as e:
            result.add_error(f"Season assignment failed: {e}")

        try:
            # Компенсационные баллы ФСМ (п.8.6.1-8.6.5) — пересчитать для
            # старого турнира тоже, если игру перепривязали к другому/сняли
            # с турнира вовсе (иначе оставшиеся игры старого турнира будут
            # использовать устаревшее games_played/i для этого игрока).
            touched_tournaments = {
                t for t in (game.tournament_id, old_tournament_id) if t
            }
            for t_id in touched_tournaments:
                RatingService.recompute_compensation_points(t_id, commit=False)
            if touched_tournaments:
                result.add_step(
                    f"Compensation points recomputed for {len(touched_tournaments)} tournament(s)"
                )
        except Exception as e:
            result.add_error(f"Compensation points failed: {e}")

        try:
            # Fantasy live points — пересчитать и для нового, и для старого
            # турнира/этапа (если игру перепривязали или сняли, драфты
            # старого турнира/серии тоже должны потерять её вклад).
            # Проверяем tournament_id И stage_id по отдельности — перенос
            # игры между двумя сериями ОДНОГО и того же серийного турнира
            # меняет только stage_id, tournament_id остаётся прежним, и
            # старая серия всё равно должна пересчитаться.
            _update_fantasy_live_points(game.tournament_id, game.stage_id)
            if old_tournament_id != game.tournament_id or old_stage_id != game.stage_id:
                _update_fantasy_live_points(old_tournament_id, old_stage_id)
            result.add_step("Fantasy live points updated")
        except Exception as e:
            result.add_error(f"Fantasy live points failed: {e}")

        try:
            rewards = EconomyService.apply_rewards_after_game(
                game, commit=False, as_of=game.played_at,
            )
            ok_count = sum(1 for r in rewards if r.ok)
            result.add_step(f"New coins distributed: {ok_count} players rewarded")
        except Exception as e:
            result.add_error(f"Coin rewards failed: {e}")

        try:
            db.session.commit()
            result.add_step("Committed all changes")
        except Exception as e:
            db.session.rollback()
            result.add_error(f"Commit failed: {e}")

        try:
            from app.services.achievement_service import AchievementService
            unlocked = AchievementService.check_after_game(game)
            newly = sum(1 for r in unlocked if r.ok and r.data)
            result.add_step(f"Achievements checked: {newly} newly unlocked")
        except Exception as e:
            result.add_error(f"Achievement check failed: {e}")

        return result


class PostTournamentOrchestrator:
    """
    Called when a tournament is marked as finished.
    Order: rating → fantasy scoring → coin rewards → season update.
    """

    @staticmethod
    def run(tournament: Tournament) -> OrchestratorResult:
        from app.services.fantasy_service import FantasyService
        from app.services.economy_service import EconomyService
        from app.services.season_service import SeasonService

        result = OrchestratorResult.empty()

        if tournament.status != "finished":
            result.add_error("Tournament is not finished yet.")
            return result

        try:
            # 1. Lock any remaining open fantasy drafts
            locked = FantasyService.lock_drafts_for_tournament(
                tournament.id, commit=True
            )
            result.add_step(f"Locked {locked} remaining fantasy drafts")
        except Exception as e:
            result.add_error(f"Fantasy lock failed: {e}")

        try:
            # 2. Score fantasy drafts
            fantasy_results = FantasyService.score_tournament(
                tournament.id, commit=True
            )
            result.add_step(f"Fantasy scored: {len(fantasy_results)} drafts")
        except Exception as e:
            result.add_error(f"Fantasy scoring failed: {e}")

        try:
            # 3. Tournament coin rewards
            coin_results = EconomyService.apply_tournament_rewards(
                tournament.id, commit=True
            )
            result.add_step(f"Tournament coins distributed: {len(coin_results)} players")
        except Exception as e:
            result.add_error(f"Tournament coin rewards failed: {e}")

        try:
            # 4. Close expired seasons (in case tournament end triggers season end)
            season_results = SeasonService.close_expired_seasons()
            closed = [r for r in season_results if r.ok]
            if closed:
                result.add_step(f"Closed {len(closed)} expired seasons")
        except Exception as e:
            result.add_error(f"Season close failed: {e}")

        try:
            # 5. Achievement checks
            from app.services.achievement_service import AchievementService
            unlocked = AchievementService.check_after_tournament(tournament)
            newly = sum(1 for r in unlocked if r.ok and r.data)
            result.add_step(f"Achievements checked: {newly} unlocked")
        except Exception as e:
            result.add_error(f"Achievement check failed: {e}")

        return result
