"""
EconomyService
==============
All coin economy logic. Immutable ledger — every change is recorded.

Anti-abuse:
- Daily cap on game_reward: max DAILY_GAME_REWARD_CAP coins per player per day.
- Admin adjustments require an explicit reason string ≥ 10 chars.
- Spending validates balance before deducting.
- All operations are atomic (flush inside transaction).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy import func

from app import db
from app.models import (
    Player, Game, GameSlot, CoinTransaction, CoinSourceType,
    Role, WinSide, EconomySettings,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Reward tables (business rules, single place to change)
# ---------------------------------------------------------------------------

# Coins awarded per game by role × outcome
GAME_REWARDS: dict[tuple[Role, bool], float] = {
    # (role, won): coins
    (Role.CIVILIAN, True):  5.0,
    (Role.CIVILIAN, False):  0.0,
    (Role.MAFIA,    True):  5.0,
    (Role.MAFIA,    False):  0.0,
    (Role.DON,      True):  5.0,
    (Role.DON,      False):  0.0,
    (Role.SHERIFF,  True):  5.0,
    (Role.SHERIFF,  False):  0.0,
}
PARTICIPATION_BONUS = 1.0      # always, just for playing

# Tournament placement rewards
TOURNAMENT_REWARDS: dict[int, float] = {
    1: 120.0,
    2: 80.0,
    3:  60.0,
    4:  40.0,
    5:  20.0,
}
TOURNAMENT_PARTICIPATION = 10.0

# Season placement rewards
SEASON_WINNER_REWARD    = 500.0
SEASON_TOP3_REWARD      = 150.0
SEASON_TOP10_REWARD     =  50.0

# Fantasy Draft — entry fee & prize pool split.
# These are the defaults used to seed EconomySettings on first access; once
# the row exists, admins can change it live from /admin/economy without a
# code change. Kept here (not just in the DB) so the intended defaults are
# documented next to the rest of the reward tables.
FANTASY_ENTRY_COST_DEFAULT         = 100.0
FANTASY_FIRST_PLACE_SHARE_DEFAULT  = 0.70
FANTASY_SECOND_PLACE_SHARE_DEFAULT = 0.30

# Anti-abuse: max coins a player can earn from games in a single day
DAILY_GAME_REWARD_CAP   = 200.0

# Стартовый бонус, начисляемый при создании нового Player.
WELCOME_BONUS_AMOUNT = 100.0

# Значение, до которого EconomyService.reset_all_balances() выставляет
# баланс каждому игроку (не 0 — по явному запросу администратора).
DEFAULT_RESET_BALANCE = 75.0

# ---------------------------------------------------------------------------
# Result DTO
# ---------------------------------------------------------------------------

@dataclass
class EconomyResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "EconomyResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "EconomyResult":
        return cls(ok=False, message=msg)


# ---------------------------------------------------------------------------
# EconomyService
# ---------------------------------------------------------------------------

class EconomyService:

    # ── Core ledger operations ────────────────────────────────────────────────

    @staticmethod
    def _get_balance(player: Player) -> float:
        return getattr(player, "coins", 0.0) or 0.0

    @staticmethod
    def _record(
        player: Player,
        amount: float,
        reason: str,
        source_type: CoinSourceType,
        ref_game_id: Optional[int] = None,
        ref_tournament_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> CoinTransaction:
        """
        Append an immutable ledger entry and update player.coins.

        created_at: только для Migration API — проставляет реальную
        историческую дату транзакции вместо "сейчас" (см.
        migration_service.py). В обычном рантайме не передаётся,
        используется дефолт колонки (datetime.now(UTC)).
        """
        new_balance = round(EconomyService._get_balance(player) + amount, 2)
        player.coins = new_balance
        # Force SQLAlchemy to track the change even if the object
        # came from a different query scope or was detached
        db.session.add(player)

        tx = CoinTransaction(
            player_id=player.id,
            amount=round(amount, 2),
            balance_after=new_balance,
            reason=reason,
            source_type=source_type,
            ref_game_id=ref_game_id,
            ref_tournament_id=ref_tournament_id,
        )
        if created_at is not None:
            tx.created_at = created_at
        db.session.add(tx)
        logger.debug(
            f"Coin tx: player#{player.id} {'+' if amount >= 0 else ''}{amount} "
            f"({source_type.value}) → balance={new_balance}"
        )
        return tx

    @staticmethod
    def add_coins(
        player: Player,
        amount: float,
        reason: str,
        source_type: CoinSourceType,
        ref_game_id: Optional[int] = None,
        ref_tournament_id: Optional[int] = None,
        commit: bool = True,
    ) -> EconomyResult:
        if amount <= 0:
            return EconomyResult.fail("amount must be positive")
        tx = EconomyService._record(
            player, amount, reason, source_type, ref_game_id, ref_tournament_id
        )
        if commit:
            db.session.commit()
        return EconomyResult.success(
            f"+{amount} монет: {reason}", data=tx
        )

    @staticmethod
    def spend_coins(
        player: Player,
        amount: float,
        reason: str,
        commit: bool = True,
    ) -> EconomyResult:
        if amount <= 0:
            return EconomyResult.fail("amount must be positive")
        if EconomyService._get_balance(player) < amount:
            return EconomyResult.fail(
                f"Недостаточно монет. Баланс: {EconomyService._get_balance(player):.0f}, нужно: {amount:.0f}"
            )
        tx = EconomyService._record(
            player, -amount, reason, CoinSourceType.PURCHASE
        )
        if commit:
            db.session.commit()
        return EconomyResult.success(f"-{amount} монет: {reason}", data=tx)

    @staticmethod
    def admin_adjust(
        player: Player,
        amount: float,
        reason: str,
        commit: bool = True,
    ) -> EconomyResult:
        """Admin manual adjustment (positive or negative)."""
        if len(reason.strip()) < 10:
            return EconomyResult.fail("Причина должна быть не короче 10 символов.")
        tx = EconomyService._record(
            player, amount, reason, CoinSourceType.ADMIN_ADJUSTMENT
        )
        if commit:
            db.session.commit()
        return EconomyResult.success(
            f"Корректировка {'+' if amount >= 0 else ''}{amount}: {reason}", data=tx
        )

    @staticmethod
    def admin_bulk_adjust(
        players: List[Player],
        amount: float,
        reason: str,
    ) -> EconomyResult:
        """Same admin adjustment applied to many players in one ledger commit."""
        if len(reason.strip()) < 10:
            return EconomyResult.fail("Причина должна быть не короче 10 символов.")
        if not players:
            return EconomyResult.fail("Не выбрано ни одного игрока.")
        if not amount:
            return EconomyResult.fail("Сумма не может быть нулевой.")

        for player in players:
            EconomyService._record(player, amount, reason, CoinSourceType.ADMIN_ADJUSTMENT)
        db.session.commit()
        return EconomyResult.success(
            f"Корректировка {'+' if amount >= 0 else ''}{amount} применена к {len(players)} игрокам: {reason}"
        )

    @staticmethod
    def grant_welcome_bonus(player: Player, commit: bool = True) -> EconomyResult:
        """
        Стартовый бонус новому игроку — единая точка входа, вызывается из
        обоих мест создания Player (players.py::add_player,
        api.py::players_quick_create). НЕ вызывается из миграции (там
        баланс сознательно не переносится и не выставляется — см.
        migration_service.py).
        """
        tx = EconomyService._record(
            player, WELCOME_BONUS_AMOUNT, "Приветственный бонус новому игроку",
            CoinSourceType.SYSTEM_BONUS,
        )
        if commit:
            db.session.commit()
        return EconomyResult.success(
            f"Начислен приветственный бонус: {WELCOME_BONUS_AMOUNT} монет.", data=tx
        )

    @staticmethod
    def reset_all_balances() -> EconomyResult:
        """
        Полный сброс экономики: удаляет ВСЮ историю CoinTransaction и
        выставляет Player.coins в DEFAULT_RESET_BALANCE у всех игроков.
        Необратимо (в отличие от остальной логики сервиса, которая ведёт
        неизменяемый леджер) — осознанное решение по явному запросу
        администратора, не вызывается автоматически ниоткуда.
        """
        tx_count = db.session.query(CoinTransaction).delete()
        player_count = db.session.query(Player).update({Player.coins: DEFAULT_RESET_BALANCE})
        db.session.commit()
        return EconomyResult.success(
            f"Баланс сброшен до {DEFAULT_RESET_BALANCE} у {player_count} игроков, "
            f"удалено записей истории: {tx_count}."
        )

    @staticmethod
    def validate_balance(player: Player, required: float) -> bool:
        return EconomyService._get_balance(player) >= required

    # ── Anti-abuse: daily cap check ───────────────────────────────────────────

    @staticmethod
    def _daily_game_earnings(player_id: int, as_of: Optional[datetime] = None) -> float:
        """
        Total game_reward coins earned by this player on the "day" of
        as_of (defaults to real now — normal runtime behavior unchanged).

        as_of: только для Migration API — при полном replay исторических
        игр (см. migration_service.py) кап должен считаться относительно
        РЕАЛЬНОЙ даты игры, а не момента переноса, иначе сотни старых игр,
        физически импортированных за пару минут, схлопнутся в одно
        "сегодня" и лимит некорректно обрежет честно заработанные награды.
        """
        reference = as_of if as_of is not None else datetime.now(timezone.utc)
        today_start = reference.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Верхняя граница нужна только когда reference — историческая дата
        # (as_of): без неё "created_at >= today_start" захватил бы всё от
        # этого дня и до реального "сейчас". Для живого рантайма (as_of не
        # передан) верхней границы никогда не было и не нужно — будущих
        # транзакций не существует, поведение не меняется.
        today_end = today_start + timedelta(days=1)
        result = (
            db.session.query(func.sum(CoinTransaction.amount))
            .filter(
                CoinTransaction.player_id == player_id,
                CoinTransaction.source_type == CoinSourceType.GAME_REWARD,
                CoinTransaction.amount > 0,
                CoinTransaction.created_at >= today_start,
                CoinTransaction.created_at < today_end,
            )
            .scalar()
        )
        return float(result or 0.0)

    # ── Game rewards ──────────────────────────────────────────────────────────

    @staticmethod
    def apply_rewards_after_game(
        game: Game, commit: bool = True, as_of: Optional[datetime] = None,
    ) -> List[EconomyResult]:
        """
        Distribute coin rewards to all participants of a finished game.
        Respects daily cap. Call after RatingService.apply_base_scores_to_game().

        as_of: только для Migration API — см. _daily_game_earnings(). При
        передаче также штампует созданные CoinTransaction этой же датой
        (иначе кап считался бы по историческому дню, а сама запись в
        леджере всё равно легла бы с датой "сейчас" — требование сохранять
        оригинальные временные поля при переносе).
        """
        if not game.is_finished:
            return [EconomyResult.fail("Игра ещё не завершена.")]
        if not game.is_ranked:
            return []

        results = []
        for slot in game.slots:
            player = slot.player
            if not player:
                continue

            # Anti-abuse: check daily cap
            earned_today = EconomyService._daily_game_earnings(player.id, as_of=as_of)
            if earned_today >= DAILY_GAME_REWARD_CAP:
                logger.warning(
                    f"Player #{player.id} hit daily cap ({earned_today}), skipping game reward"
                )
                results.append(EconomyResult.fail(
                    f"{player.display_name}: дневной лимит монет достигнут"
                ))
                continue

            # Determine if player won
            won = (
                (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
                or (slot.is_city_side and game.win_side == WinSide.CITY)
            )

            reward = GAME_REWARDS.get((slot.role, won), 0.0) + PARTICIPATION_BONUS

            # Clamp to daily cap
            remaining_cap = DAILY_GAME_REWARD_CAP - earned_today
            reward = min(reward, remaining_cap)

            EconomyService._record(
                player,
                reward,
                f"{'Победа' if won else 'Участие'} в игре #{game.id} ({slot.role.value})",
                CoinSourceType.GAME_REWARD,
                ref_game_id=game.id,
                created_at=as_of,
            )
            results.append(EconomyResult.success(
                f"{player.display_name} +{reward} монет", data=player
            ))

        if commit:
            db.session.commit()
        return results

    # ── Tournament rewards ────────────────────────────────────────────────────

    @staticmethod
    def apply_tournament_rewards(tournament_id: int, commit: bool = True) -> List[EconomyResult]:
        """
        Distribute coins based on final tournament standings.
        Call after tournament is marked finished.
        """
        from app.services.rating_service import RatingService
        from app.models import Tournament, Player

        t = db.session.get(Tournament, tournament_id)
        if not t or t.status != "finished":
            return [EconomyResult.fail("Турнир не завершён.")]

        ratings = RatingService.get_tournament_rating(tournament_id)
        results = []

        for r in ratings:
            player = db.session.get(Player, r.player_id)
            if not player:
                continue

            # Participation reward
            EconomyService._record(
                player,
                TOURNAMENT_PARTICIPATION,
                f"Участие в турнире «{t.name}»",
                CoinSourceType.TOURNAMENT_REWARD,
                ref_tournament_id=tournament_id,
            )

            # Placement reward
            placement_reward = TOURNAMENT_REWARDS.get(r.rank, 0.0)
            if placement_reward > 0:
                EconomyService._record(
                    player,
                    placement_reward,
                    f"Место #{r.rank} в турнире «{t.name}»",
                    CoinSourceType.TOURNAMENT_REWARD,
                    ref_tournament_id=tournament_id,
                )

            results.append(EconomyResult.success(
                f"{r.display_name}: +{TOURNAMENT_PARTICIPATION + TOURNAMENT_REWARDS.get(r.rank, 0)}"
            ))

        if commit:
            db.session.commit()
        return results

    # ── Season rewards ────────────────────────────────────────────────────────

    @staticmethod
    def apply_season_rewards(season_id: int, commit: bool = True) -> List[EconomyResult]:
        """Call after season is closed and winner determined."""
        from app.services.rating_service import RatingService
        from app.models import Season, Player

        season = db.session.get(Season, season_id)
        if not season or not season.winner_player_id:
            return [EconomyResult.fail("Сезон не завершён или победитель не определён.")]

        ratings = RatingService.get_season_rating(season_id)
        results = []

        from app.services.bot_notify_service import BotNotifyService

        for r in ratings:
            player = db.session.get(Player, r.player_id)
            if not player:
                continue

            if r.rank == 1:
                amount, desc = SEASON_WINNER_REWARD, f"🏆 Победа в сезоне «{season.name}»"
            elif r.rank <= 3:
                amount, desc = SEASON_TOP3_REWARD, f"Топ-3 сезона «{season.name}»"
            elif r.rank <= 10:
                amount, desc = SEASON_TOP10_REWARD, f"Топ-10 сезона «{season.name}»"
            else:
                continue

            EconomyService._record(
                player, amount, desc, CoinSourceType.SEASON_REWARD
            )
            results.append(EconomyResult.success(f"{r.display_name}: +{amount}"))

            BotNotifyService.notify_player(
                player.id, "season-award",
                {"season_name": season.name, "rank": r.rank, "amount": amount},
            )

        if commit:
            db.session.commit()
        return results

    # ── Economy settings (admin-editable) ────────────────────────────────────

    @staticmethod
    def get_settings() -> EconomySettings:
        """Return the single EconomySettings row, creating it with defaults
        on first access."""
        settings = db.session.query(EconomySettings).first()
        if not settings:
            settings = EconomySettings(
                fantasy_entry_cost=FANTASY_ENTRY_COST_DEFAULT,
                fantasy_first_place_share=FANTASY_FIRST_PLACE_SHARE_DEFAULT,
                fantasy_second_place_share=FANTASY_SECOND_PLACE_SHARE_DEFAULT,
            )
            db.session.add(settings)
            db.session.commit()
        return settings

    @staticmethod
    def update_settings(
        fantasy_entry_cost: Optional[float] = None,
        fantasy_first_place_share: Optional[float] = None,
        fantasy_second_place_share: Optional[float] = None,
    ) -> EconomyResult:
        """Admin update of economy settings. Only provided fields are changed."""
        settings = EconomyService.get_settings()

        if fantasy_entry_cost is not None:
            if fantasy_entry_cost <= 0:
                return EconomyResult.fail("Стоимость участия должна быть положительной.")
            settings.fantasy_entry_cost = round(fantasy_entry_cost, 2)

        if fantasy_first_place_share is not None:
            if not (0 <= fantasy_first_place_share <= 1):
                return EconomyResult.fail("Доля за 1-е место должна быть от 0% до 100%.")
            settings.fantasy_first_place_share = round(fantasy_first_place_share, 4)

        if fantasy_second_place_share is not None:
            if not (0 <= fantasy_second_place_share <= 1):
                return EconomyResult.fail("Доля за 2-е место должна быть от 0% до 100%.")
            settings.fantasy_second_place_share = round(fantasy_second_place_share, 4)

        # Never allow the pool to pay out more than it collected.
        if settings.fantasy_first_place_share + settings.fantasy_second_place_share > 1.0001:
            return EconomyResult.fail(
                "Сумма долей 1-го и 2-го места не может превышать 100%."
            )

        db.session.commit()
        return EconomyResult.success("Настройки Fantasy обновлены.", data=settings)

    # ── Queries ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_balance(player: Player) -> float:
        return EconomyService._get_balance(player)

    @staticmethod
    def get_history(player_id: int, limit: int = 50) -> List[CoinTransaction]:
        return (
            db.session.query(CoinTransaction)
            .filter_by(player_id=player_id)
            .order_by(CoinTransaction.created_at.desc())
            .limit(limit)
            .all()
        )
