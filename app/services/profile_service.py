"""
ProfileService
==============
Extended player/user profile logic.
All derived statistics, history, and profile mutations go here.
No rating recalculation — delegates to RatingService.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict

from app import db
from app.models import Player, Game, GameSlot, Role, WinSide, Season, CoinTransaction, PlayerAchievement

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------

@dataclass
class RoleBreakdown:
    role: str
    games: int
    wins: int
    total_score: float
    win_rate: float

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "games": self.games,
            "wins": self.wins,
            "total_score": round(self.total_score, 2),
            "win_rate": round(self.win_rate, 1),
        }


@dataclass
class PlayerExtendedStats:
    player_id: int
    display_name: str
    total_games: int = 0
    total_wins: int = 0
    win_rate: float = 0.0
    total_score: float = 0.0
    avg_score: float = 0.0
    elo: float = 1000.0
    coins: float = 0.0
    best_score: float = 0.0
    worst_score: float = 0.0
    current_streak: int = 0   # consecutive wins (0 if last game was a loss)
    longest_streak: int = 0   # longest win streak
    longest_loss_streak: int = 0
    current_streak_signed: int = 0  # positive = win streak, negative = loss streak
    role_breakdown: List[RoleBreakdown] = field(default_factory=list)
    monthly_games: Dict[str, int] = field(default_factory=dict)  # "YYYY-MM" → count
    tournament_count: int = 0
    tournament_wins: int = 0
    season_wins: int = 0
    lh_total: float = 0.0        # сумма ЛХ-баллов (бонус за успешный ПУ-звонок)
    pu_count: int = 0            # раз был ПУ (первым убитым)
    pu_sheriff_count: int = 0    # из них — играя за шерифа
    pu_accuracy: Optional[float] = None  # % угаданных мафий (из 3 названных подозреваемых) за игры в роли ПУ
    best_day_wins: Optional[dict] = None    # {"date": "YYYY-MM-DD", "wins": N, "games": M}
    best_day_bonus: Optional[dict] = None   # {"date": "YYYY-MM-DD", "bonus": X}

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "display_name": self.display_name,
            "total_games": self.total_games,
            "total_wins": self.total_wins,
            "win_rate": round(self.win_rate, 1),
            "total_score": round(self.total_score, 2),
            "avg_score": round(self.avg_score, 2),
            "elo": round(self.elo, 1),
            "coins": round(self.coins, 2),
            "best_score": round(self.best_score, 2),
            "worst_score": round(self.worst_score, 2),
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "longest_loss_streak": self.longest_loss_streak,
            "current_streak_signed": self.current_streak_signed,
            "tournament_count": self.tournament_count,
            "tournament_wins": self.tournament_wins,
            "season_wins": self.season_wins,
            "lh_total": round(self.lh_total, 2),
            "pu_count": self.pu_count,
            "pu_sheriff_count": self.pu_sheriff_count,
            "pu_accuracy": self.pu_accuracy,
            "best_day_wins": self.best_day_wins,
            "best_day_bonus": self.best_day_bonus,
            "role_breakdown": [r.to_dict() for r in self.role_breakdown],
            "monthly_games": self.monthly_games,
        }


@dataclass
class ProfileResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "ProfileResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "ProfileResult":
        return cls(ok=False, message=msg)


# ---------------------------------------------------------------------------
# ProfileService
# ---------------------------------------------------------------------------

class ProfileService:

    # ── Profile updates ───────────────────────────────────────────────────────

    @staticmethod
    def update_profile(
        player: Player,
        nickname: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> ProfileResult:
        if nickname is not None:
            nickname = nickname.strip() or None
            # Check uniqueness
            if nickname:
                conflict = db.session.query(Player).filter(
                    Player.nickname == nickname,
                    Player.id != player.id,
                ).first()
                if conflict:
                    return ProfileResult.fail(f"Никнейм «{nickname}» уже занят.")
            player.nickname = nickname

        if bio is not None:
            bio = bio.strip()[:500]  # max 500 chars
            player.bio = bio

        if avatar_url is not None:
            avatar_url = avatar_url.strip()[:512] or None
            player.avatar_url = avatar_url

        db.session.commit()
        return ProfileResult.success("Профиль обновлён.", data=player)

    # ── Extended stats ────────────────────────────────────────────────────────

    @staticmethod
    def get_extended_stats(player_id: int) -> Optional[PlayerExtendedStats]:
        player = db.session.get(Player, player_id)
        if not player:
            return None

        slots = (
            db.session.query(GameSlot)
            .join(Game)
            .filter(
                GameSlot.player_id == player_id,
                Game.is_finished == True,
            )
            .order_by(Game.played_at.asc())
            .all()
        )

        stats = PlayerExtendedStats(
            player_id=player.id,
            display_name=player.display_name,
            elo=player.elo,
            coins=getattr(player, "coins", 0.0) or 0.0,
        )

        # Role breakdown accumulator
        role_data: Dict[str, dict] = {}

        win_streak = 0
        max_win_streak = 0
        loss_streak = 0
        max_loss_streak = 0
        stats.worst_score = None  # sentinel until first slot seen

        # По календарным дням (не месяцам) — для "самых успешных дней".
        day_wins: Dict[str, int] = {}
        day_games: Dict[str, int] = {}
        day_bonus: Dict[str, float] = {}

        pu_mafia_total = 0  # сумма pu_mafia_count по всем играм в роли ПУ — для точности ПУ

        for slot in slots:
            game = slot.game
            won = (
                (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
                or (slot.is_city_side and game.win_side == WinSide.CITY)
            )

            stats.total_games += 1
            stats.total_score += slot.total_score
            stats.best_score = max(stats.best_score, slot.total_score)
            stats.worst_score = slot.total_score if stats.worst_score is None else min(stats.worst_score, slot.total_score)

            if won:
                stats.total_wins += 1
                win_streak += 1
                max_win_streak = max(max_win_streak, win_streak)
                loss_streak = 0
            else:
                loss_streak += 1
                max_loss_streak = max(max_loss_streak, loss_streak)
                win_streak = 0

            # ПУ (первым убитый) — считается "страшным" для мафии: его убивают
            # в первую же ночь. Отдельно считаем комбо ПУ+Шериф — шерифа
            # обычно убивают первым, если мафия его вычислила.
            if slot.is_pu:
                stats.pu_count += 1
                pu_mafia_total += slot.pu_mafia_count or 0
                stats.lh_total += slot.pu_bonus
                if slot.role == Role.SHERIFF:
                    stats.pu_sheriff_count += 1

            # Role breakdown
            rname = slot.role.value
            if rname not in role_data:
                role_data[rname] = {"games": 0, "wins": 0, "score": 0.0}
            role_data[rname]["games"] += 1
            role_data[rname]["score"] += slot.total_score
            if won:
                role_data[rname]["wins"] += 1

            # Monthly activity
            month_key = game.played_at.strftime("%Y-%m")
            stats.monthly_games[month_key] = stats.monthly_games.get(month_key, 0) + 1

            # Daily activity (для "лучших дней")
            day_key = game.played_at.strftime("%Y-%m-%d")
            day_games[day_key] = day_games.get(day_key, 0) + 1
            if won:
                day_wins[day_key] = day_wins.get(day_key, 0) + 1
            day_bonus[day_key] = day_bonus.get(day_key, 0.0) + (slot.bonus_score or 0.0)

        stats.current_streak = win_streak
        stats.longest_streak = max_win_streak
        stats.longest_loss_streak = max_loss_streak
        stats.current_streak_signed = win_streak if win_streak > 0 else -loss_streak
        stats.worst_score = stats.worst_score or 0.0

        if day_wins:
            best_day, wins_that_day = max(day_wins.items(), key=lambda kv: kv[1])
            stats.best_day_wins = {
                "date": best_day, "wins": wins_that_day, "games": day_games[best_day],
            }
        if day_bonus:
            best_day, bonus_that_day = max(day_bonus.items(), key=lambda kv: kv[1])
            if bonus_that_day > 0:
                stats.best_day_bonus = {"date": best_day, "bonus": round(bonus_that_day, 2)}

        if stats.pu_count > 0:
            # Каждая ПУ-игра — ровно 3 названных подозреваемых, так что доля
            # угаданных из них — валидный процент точности (не "средний улов").
            stats.pu_accuracy = round(pu_mafia_total / (stats.pu_count * 3) * 100, 1)

        if stats.total_games > 0:
            stats.win_rate = round(stats.total_wins / stats.total_games * 100, 1)
            stats.avg_score = round(stats.total_score / stats.total_games, 2)

        stats.role_breakdown = [
            RoleBreakdown(
                role=rname,
                games=d["games"],
                wins=d["wins"],
                total_score=d["score"],
                win_rate=round(d["wins"] / d["games"] * 100, 1) if d["games"] else 0.0,
            )
            for rname, d in role_data.items()
        ]

        # Tournament count
        from app.models import TournamentParticipant
        stats.tournament_count = db.session.query(TournamentParticipant).filter_by(
            player_id=player_id
        ).count()

        # Season wins
        stats.season_wins = db.session.query(Season).filter_by(
            winner_player_id=player_id
        ).count()

        stats.tournament_wins = ProfileService._count_tournament_wins(player_id)

        return stats

    @staticmethod
    def _count_tournament_wins(player_id: int) -> int:
        """Сколько ЗАВЕРШЁННЫХ турниров игрок выиграл (1-е место в общем
        зачёте турнира) за всю историю — не путать с tournament_count
        (участие). Тот же паттерн "перебрать все финальные турниры и
        спросить рейтинг", что уже используется в NominationService
        (_cup_king) — недёшево при большом числе турниров, но это разовый
        расчёт для страницы сравнения, не горячий путь."""
        from app.models import Tournament
        from app.services.rating_service import RatingService

        tournaments = db.session.query(Tournament).filter(Tournament.status == "finished").all()
        wins = 0
        for t in tournaments:
            ratings = RatingService.get_tournament_rating(t.id)
            champion = next((r for r in ratings if r.rank == 1), None)
            if champion and champion.player_id == player_id:
                wins += 1
        return wins

    # ── Game history ──────────────────────────────────────────────────────────

    @staticmethod
    def get_game_history(
        player_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[GameSlot]:
        return (
            db.session.query(GameSlot)
            .join(Game)
            .filter(
                GameSlot.player_id == player_id,
                Game.is_finished == True,
            )
            .order_by(Game.played_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_economy_history(player_id: int, limit: int = 30) -> List[CoinTransaction]:
        return (
            db.session.query(CoinTransaction)
            .filter_by(player_id=player_id)
            .order_by(CoinTransaction.created_at.desc())
            .limit(limit)
            .all()
        )

    # ── Head-to-head ──────────────────────────────────────────────────────────

    @staticmethod
    def head_to_head(player_id_a: int, player_id_b: int) -> dict:
        """
        Games where both players participated.
        Returns win/loss/draw breakdown for player_a perspective.
        """
        # Games containing both players
        games_a = {
            s.game_id: s
            for s in db.session.query(GameSlot)
            .join(Game)
            .filter(GameSlot.player_id == player_id_a, Game.is_finished == True)
            .all()
        }
        games_b = {
            s.game_id: s
            for s in db.session.query(GameSlot)
            .join(Game)
            .filter(GameSlot.player_id == player_id_b, Game.is_finished == True)
            .all()
        }
        shared = set(games_a) & set(games_b)

        wins = losses = draws = 0
        for gid in shared:
            slot_a = games_a[gid]
            game = slot_a.game
            a_won = (
                (slot_a.is_mafia_side and game.win_side == WinSide.MAFIA)
                or (slot_a.is_city_side and game.win_side == WinSide.CITY)
            )
            slot_b = games_b[gid]
            b_won = (
                (slot_b.is_mafia_side and game.win_side == WinSide.MAFIA)
                or (slot_b.is_city_side and game.win_side == WinSide.CITY)
            )
            if a_won and not b_won:
                wins += 1
            elif b_won and not a_won:
                losses += 1
            else:
                draws += 1

        return {
            "player_a": player_id_a,
            "player_b": player_id_b,
            "shared_games": len(shared),
            "wins": wins,
            "losses": losses,
            "draws": draws,
        }

    # ── New Profile page: cheap aggregator ──────────────────────────────────────

    @staticmethod
    def get_profile(player_id: int) -> Optional[dict]:
        """
        Cheap main-page read: Player row + one aggregate query for
        games/wins + equipped customization + pinned achievements + global
        rank. Deliberately does NOT run the full statistics slot-loop —
        that lives behind get_statistics()/the /statistics sub-page.
        """
        player = db.session.get(Player, player_id)
        if not player:
            return None

        from sqlalchemy import case, func
        from app.services.shop_service import ShopService
        from app.services.rating_service import RatingService

        row = (
            db.session.query(
                func.count(GameSlot.id),
                func.sum(
                    case(
                        (
                            (
                                GameSlot.role.in_([Role.MAFIA, Role.DON])
                                & (Game.win_side == WinSide.MAFIA)
                            )
                            | (
                                GameSlot.role.in_([Role.CIVILIAN, Role.SHERIFF])
                                & (Game.win_side == WinSide.CITY)
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
            )
            .join(Game)
            .filter(GameSlot.player_id == player_id, Game.is_finished == True)
            .one()
        )
        total_games = row[0] or 0
        total_wins = row[1] or 0
        win_rate = round(total_wins / total_games * 100, 1) if total_games else 0.0

        equipped = ShopService.get_equipped(player_id)
        customization = {
            slot: {"inventory_item_id": inv.id, "item": inv.item.to_dict()}
            for slot, inv in equipped.items()
        }

        pinned = (
            db.session.query(PlayerAchievement)
            .filter_by(player_id=player_id, pinned=True)
            .order_by(PlayerAchievement.pinned_order)
            .all()
        )

        rating = RatingService.get_player_rating(player_id)

        from app.services.title_service import TitleService
        equipped_title = TitleService.get_equipped_title(player_id)

        return {
            "player": player.to_dict(),
            "bio": player.bio,
            "avatar_url": player.avatar_url,
            "coins": getattr(player, "coins", 0.0) or 0.0,
            "total_games": total_games,
            "total_wins": total_wins,
            "win_rate": win_rate,
            "elo": player.elo,
            "global_rank": rating.rank if rating else None,
            "customization": customization,
            "pinned_achievements": [pa.to_dict() for pa in pinned],
            "equipped_title": equipped_title.to_dict() if equipped_title else None,
        }

    # ── /statistics sub-page ─────────────────────────────────────────────────────

    @staticmethod
    def get_statistics(player_id: int) -> Optional[PlayerExtendedStats]:
        """Thin wrapper — the full single-pass computation."""
        return ProfileService.get_extended_stats(player_id)

    @staticmethod
    def get_role_statistics(player_id: int) -> Optional[dict]:
        """Derived from the same single-pass computation as get_statistics()
        — no extra query."""
        stats = ProfileService.get_extended_stats(player_id)
        if not stats:
            return None

        roles = stats.role_breakdown
        favorite_role = max(roles, key=lambda r: r.games, default=None)
        # Require a minimum sample before crowning a "best"/"worst" role,
        # to avoid a single lucky/unlucky game deciding it.
        eligible = [r for r in roles if r.games >= 3] or roles
        best_role = max(eligible, key=lambda r: r.win_rate, default=None)
        worst_role = min(eligible, key=lambda r: r.win_rate, default=None)

        return {
            "role_breakdown": [r.to_dict() for r in roles],
            "favorite_role": favorite_role.to_dict() if favorite_role else None,
            "best_role": best_role.to_dict() if best_role else None,
            "worst_role": worst_role.to_dict() if worst_role else None,
            "best_win_streak": stats.longest_streak,
            "worst_loss_streak": stats.longest_loss_streak,
            "current_streak_signed": stats.current_streak_signed,
            "avg_score": stats.avg_score,
            "best_score": stats.best_score,
            "worst_score": stats.worst_score,
        }

    @staticmethod
    def get_comparison_stats(player_id: int) -> Optional[dict]:
        """
        Сравнение игрока с клубом: средние по клубу значения + перцентиль
        (какой % ранжированных игроков этот игрок обходит) по ELO/винрейту/
        среднему баллу. Переиспользует RatingService.compute_all_ratings()
        (тот же расчёт, что и общий рейтинг/лидерборд) вместо отдельного
        агрегирующего запроса — один и тот же источник правды.
        """
        from app.services.rating_service import RatingService

        ratings = RatingService.compute_all_ratings()
        if not ratings:
            return None
        mine = next((r for r in ratings if r.player_id == player_id), None)
        if not mine:
            return None

        n = len(ratings)

        def percentile(value: float, values: List[float]) -> float:
            below = sum(1 for v in values if v < value)
            return round(below / len(values) * 100, 1)

        elos = [r.elo for r in ratings]
        wrs = [r.win_rate for r in ratings]
        scores = [r.avg_score for r in ratings]
        games = [r.games_played for r in ratings]

        return {
            "total_ranked_players": n,
            "rank": mine.rank,
            "elo": round(mine.elo, 1),
            "club_avg_elo": round(sum(elos) / n, 1),
            "elo_percentile": percentile(mine.elo, elos),
            "win_rate": round(mine.win_rate, 1),
            "club_avg_win_rate": round(sum(wrs) / n, 1),
            "win_rate_percentile": percentile(mine.win_rate, wrs),
            "avg_score": round(mine.avg_score, 2),
            "club_avg_score": round(sum(scores) / n, 2),
            "avg_score_percentile": percentile(mine.avg_score, scores),
            "games_played": mine.games_played,
            "club_avg_games": round(sum(games) / n, 1),
        }

    # Категории для карточек-дуэлей/счёта на странице сравнения — один
    # источник правды для и score-подсчёта, и карточек, и радара очков.
    # higher_better=False там, где чаще выступать в этой роли/чаще быть
    # ПУ не является преимуществом (см. тот же выбор в старом compare.html).
    _COMPARE_CATEGORIES = [
        ("elo", "ELO", "", True, 1),
        ("win_rate", "Винрейт", "%", True, 1),
        ("avg_score", "Средний балл", "", True, 2),
        ("pu_count", "Раз был ПУ", "", False, 0),
        ("lh_total", "ЛХ (очки)", "", True, 2),
        ("longest_streak", "Лучшая серия побед", "", True, 0),
    ]

    @staticmethod
    def compare_players(player_id_a: int, player_id_b: int) -> Optional[dict]:
        """
        Прямое сравнение двух ЛЮБЫХ игроков (не обязательно текущего
        пользователя) по одному и тому же набору метрик, что и остальная
        статистика — переиспользует get_statistics/get_role_statistics/
        get_comparison_stats/head_to_head для каждого вместо отдельного
        агрегирующего запроса. Дополнительно строит категории с подсчётом
        счёта, вероятность победы (по формуле Эло) и текстовый разбор —
        всё чисто детерминированное, без внешних вызовов.
        """
        player_a = db.session.get(Player, player_id_a)
        player_b = db.session.get(Player, player_id_b)
        if not player_a or not player_b:
            return None

        stats_a = ProfileService.get_statistics(player_id_a)
        stats_b = ProfileService.get_statistics(player_id_b)
        if not stats_a or not stats_b:
            return None

        h2h = ProfileService.head_to_head(player_id_a, player_id_b)

        a = stats_a.to_dict()
        b = stats_b.to_dict()

        from app.services.chart_data_service import ChartDataService
        elo_history_a = ChartDataService.get_elo_history(player_id_a)
        elo_history_b = ChartDataService.get_elo_history(player_id_b)

        categories, score = ProfileService._build_comparison_categories(a, b)
        win_prob_a = ProfileService._elo_win_probability(a["elo"], b["elo"])
        analysis = ProfileService._build_comparison_analysis(
            player_a.display_name, player_b.display_name, categories, score, win_prob_a,
        )

        return {
            "player_a": player_a,
            "player_b": player_b,
            "stats_a": a,
            "stats_b": b,
            "role_a": ProfileService.get_role_statistics(player_id_a),
            "role_b": ProfileService.get_role_statistics(player_id_b),
            "rating_a": ProfileService.get_comparison_stats(player_id_a),
            "rating_b": ProfileService.get_comparison_stats(player_id_b),
            "head_to_head": h2h if h2h["shared_games"] > 0 else None,
            "elo_history_a": elo_history_a,
            "elo_history_b": elo_history_b,
            "win_probability_a": win_prob_a,
            "win_probability_b": round(100 - win_prob_a, 1),
            "categories": categories,
            "score": score,
            "analysis": analysis,
        }

    @staticmethod
    def _elo_win_probability(elo_a: float, elo_b: float) -> float:
        """Классическая логистическая формула Эло — та же форма, что и
        EloEngine.compute_expected_result, только для отображения (не
        участвует в реальном начислении рейтинга)."""
        return round(100 / (1 + 10 ** ((elo_b - elo_a) / 400.0)), 1)

    @staticmethod
    def _build_comparison_categories(a: dict, b: dict) -> tuple[list, dict]:
        """Строит список карточек-категорий (значение А/Б, разница,
        победитель) + счёт побед по категориям — единственное место, где
        решается "кто лучше по каждой метрике" (шаблон только отображает)."""
        categories = []
        score = {"a": 0, "b": 0}
        for key, label, unit, higher_better, decimals in ProfileService._COMPARE_CATEGORIES:
            val_a = a.get(key) or 0
            val_b = b.get(key) or 0
            if val_a == val_b:
                winner = None
            elif (val_a > val_b) == higher_better:
                winner = "a"
            else:
                winner = "b"
            if winner == "a":
                score["a"] += 1
            elif winner == "b":
                score["b"] += 1

            def _fmt(v: float) -> float | int:
                return int(round(v)) if decimals == 0 else round(v, decimals)

            categories.append({
                "key": key, "label": label, "unit": unit, "decimals": decimals,
                "value_a": _fmt(val_a), "value_b": _fmt(val_b),
                "winner": winner, "diff": _fmt(abs(val_a - val_b)),
                "max_value": max(val_a, val_b) or 1,
            })
        return categories, score

    @staticmethod
    def _build_comparison_analysis(
        name_a: str, name_b: str, categories: list, score: dict, win_prob_a: float,
    ) -> dict:
        """Детерминированный (без AI) текстовый разбор — собирается из уже
        посчитанных категорий по простым правилам, а не генерируется
        внешней моделью."""
        if score["a"] == score["b"]:
            leader, leader_name, opponent_name = None, None, None
        elif score["a"] > score["b"]:
            leader, leader_name, opponent_name = "a", name_a, name_b
        else:
            leader, leader_name, opponent_name = "b", name_b, name_a

        if leader is None:
            return {
                "leader": None,
                "summary": f"{name_a} и {name_b} идут почти вровень — {score['a']}:{score['b']} по категориям.",
                "strengths": [],
                "weaknesses": [],
                "win_probability": win_prob_a if win_prob_a >= 50 else round(100 - win_prob_a, 1),
            }

        strengths = [c["label"] for c in categories if c["winner"] == leader]
        weaknesses = [c["label"] for c in categories if c["winner"] is not None and c["winner"] != leader]
        win_probability = win_prob_a if leader == "a" else round(100 - win_prob_a, 1)

        return {
            "leader": leader,
            "leader_name": leader_name,
            "summary": (
                f"{leader_name} превосходит {opponent_name} по большинству ключевых "
                f"показателей — {max(score['a'], score['b'])}:{min(score['a'], score['b'])} по категориям."
            ),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "win_probability": win_probability,
        }

    # ── Shared aggregation (used by both get_partner_statistics and
    #    get_rivalry_statistics — the query + Python pass is identical,
    #    only the derived "top N" picks differ) ─────────────────────────────

    @staticmethod
    def _compute_partner_aggregates(player_id: int) -> tuple[Dict[int, dict], Dict[int, Player]]:
        """
        O(games) — exactly 2 aggregation queries regardless of games count:
        (1) the player's own finished slots (game_id, role, win_side),
        (2) every other slot in those same game_ids. One Python pass builds
        a per-other-player aggregate, role-aware (needed for mafia-duo /
        sheriff-vs-don angles in get_rivalry_statistics, not just the
        generic same-side/opposite-side split get_partner_statistics uses).
        """
        own_rows = (
            db.session.query(GameSlot.game_id, GameSlot.role, Game.win_side)
            .join(Game)
            .filter(GameSlot.player_id == player_id, Game.is_finished == True)
            .all()
        )
        if not own_rows:
            return {}, {}

        game_ids = [r[0] for r in own_rows]
        own_by_game: Dict[int, tuple] = {}
        for game_id, role, win_side in own_rows:
            is_mafia_side = role in (Role.MAFIA, Role.DON)
            is_city_side = role in (Role.CIVILIAN, Role.SHERIFF)
            won = (is_mafia_side and win_side == WinSide.MAFIA) or (is_city_side and win_side == WinSide.CITY)
            own_by_game[game_id] = (role, is_mafia_side, won)

        co_rows = (
            db.session.query(GameSlot.game_id, GameSlot.player_id, GameSlot.role)
            .filter(GameSlot.game_id.in_(game_ids), GameSlot.player_id != player_id)
            .all()
        )

        agg: Dict[int, dict] = {}
        for game_id, other_player_id, other_role in co_rows:
            own_role, own_is_mafia, own_won = own_by_game.get(game_id, (None, None, None))
            if own_role is None:
                continue
            other_is_mafia = other_role in (Role.MAFIA, Role.DON)
            same_side = other_is_mafia == own_is_mafia

            a = agg.setdefault(other_player_id, {
                "games_together": 0, "times_ally": 0, "times_opponent": 0,
                "wins_as_ally": 0, "losses_as_ally": 0, "wins_vs": 0, "losses_vs": 0,
                "mafia_duo_games": 0, "mafia_duo_wins": 0,
                "sheriff_vs_don_games": 0, "sheriff_vs_don_wins": 0,   # own=SHERIFF, other=DON
                "don_vs_sheriff_games": 0, "don_vs_sheriff_wins": 0,   # own=DON, other=SHERIFF
            })
            a["games_together"] += 1
            if same_side:
                a["times_ally"] += 1
                if own_won:
                    a["wins_as_ally"] += 1
                else:
                    a["losses_as_ally"] += 1
                if own_is_mafia:  # both on mafia side together
                    a["mafia_duo_games"] += 1
                    if own_won:
                        a["mafia_duo_wins"] += 1
            else:
                a["times_opponent"] += 1
                if own_won:
                    a["wins_vs"] += 1
                else:
                    a["losses_vs"] += 1
                if own_role == Role.SHERIFF and other_role == Role.DON:
                    a["sheriff_vs_don_games"] += 1
                    if own_won:
                        a["sheriff_vs_don_wins"] += 1
                elif own_role == Role.DON and other_role == Role.SHERIFF:
                    a["don_vs_sheriff_games"] += 1
                    if own_won:
                        a["don_vs_sheriff_wins"] += 1

        if not agg:
            return {}, {}

        other_ids = list(agg.keys())
        players = {
            p.id: p for p in db.session.query(Player).filter(Player.id.in_(other_ids)).all()
        }
        return agg, players

    @staticmethod
    def get_partner_statistics(player_id: int, min_shared_games: int = 3) -> dict:
        empty = {
            "best_partner": None, "worst_partner": None,
            "most_frequent_ally": None, "most_frequent_opponent": None,
            "best_wr_opponent": None, "worst_wr_opponent": None,
            "min_shared_games": min_shared_games,
        }

        agg, players = ProfileService._compute_partner_aggregates(player_id)
        if not agg:
            return empty

        def make_entry(pid: int, d: dict) -> dict:
            wr_vs = round(d["wins_vs"] / d["times_opponent"] * 100, 1) if d["times_opponent"] else None
            return {
                "player_id": pid,
                "display_name": players[pid].display_name if pid in players else "?",
                **d,
                "win_rate_vs": wr_vs,
            }

        entries = [make_entry(pid, d) for pid, d in agg.items()]

        # min_shared_games отсекает случайные пары от шума — без этого порога
        # единственная сыгранная вместе игра (тем более выигранная) тривиально
        # "побеждает" по любому счётчику/проценту и подписывается как "лучший
        # напарник", хотя это статистический шум, а не реальная сыгранность.
        # Применяем один и тот же порог ко ВСЕМ частотным полям этой функции,
        # не только к WR-метрикам, которые уже были им защищены.
        eligible_allies = [e for e in entries if e["times_ally"] >= min_shared_games]
        eligible_opponents = [e for e in entries if e["times_opponent"] >= min_shared_games]

        best_partner = max(
            (e for e in eligible_allies if e["wins_as_ally"] > 0),
            key=lambda e: e["wins_as_ally"], default=None,
        )
        worst_partner = max(
            (e for e in eligible_allies if e["losses_as_ally"] > 0),
            key=lambda e: e["losses_as_ally"], default=None,
        )
        most_frequent_ally = max(eligible_allies, key=lambda e: e["times_ally"], default=None)
        most_frequent_opponent = max(eligible_opponents, key=lambda e: e["times_opponent"], default=None)

        best_wr_opponent = max(eligible_opponents, key=lambda e: e["win_rate_vs"], default=None)
        worst_wr_opponent = min(eligible_opponents, key=lambda e: e["win_rate_vs"], default=None)

        return {
            "best_partner": best_partner,
            "worst_partner": worst_partner,
            "most_frequent_ally": most_frequent_ally,
            "most_frequent_opponent": most_frequent_opponent,
            "best_wr_opponent": best_wr_opponent,
            "worst_wr_opponent": worst_wr_opponent,
            "min_shared_games": min_shared_games,
        }

    # ── Rivalry / Social (Phase 3) ───────────────────────────────────────────

    @staticmethod
    def get_rivalry_statistics(player_id: int, min_shared_games: int = 3) -> dict:
        """
        Builds on the same shared aggregate as get_partner_statistics — zero
        extra queries. Adds nemesis/favorite-victim (re-exposed win-rate-vs
        numbers under rivalry naming), WR-based best/worst teammate, mafia-duo
        stats and sheriff-vs-don rivalry (role-specific angles that partner
        statistics doesn't surface).
        """
        empty = {
            "nemesis": None, "favorite_victim": None,
            "best_teammate_wr": None, "worst_teammate_wr": None,
            "mafia_duo": None, "sheriff_vs_don": None,
            "most_played_against": None, "min_shared_games": min_shared_games,
        }

        agg, players = ProfileService._compute_partner_aggregates(player_id)
        if not agg:
            return empty

        def name(pid: int) -> str:
            return players[pid].display_name if pid in players else "?"

        entries = []
        for pid, d in agg.items():
            wr_vs = round(d["wins_vs"] / d["times_opponent"] * 100, 1) if d["times_opponent"] else None
            wr_ally = round(d["wins_as_ally"] / d["times_ally"] * 100, 1) if d["times_ally"] else None
            entries.append({"player_id": pid, "display_name": name(pid), **d, "win_rate_vs": wr_vs, "win_rate_ally": wr_ally})

        eligible_opponents = [e for e in entries if e["times_opponent"] >= min_shared_games]
        nemesis = min(eligible_opponents, key=lambda e: e["win_rate_vs"], default=None)
        favorite_victim = max(eligible_opponents, key=lambda e: e["win_rate_vs"], default=None)

        eligible_allies = [e for e in entries if e["times_ally"] >= min_shared_games]
        best_teammate_wr = max(eligible_allies, key=lambda e: e["win_rate_ally"], default=None)
        worst_teammate_wr = min(eligible_allies, key=lambda e: e["win_rate_ally"], default=None)

        most_played_against = max(eligible_opponents, key=lambda e: e["times_opponent"], default=None)

        # Дуэт мафии / Шериф-vs-Дон — узкие подкатегории (пересечение роли И
        # стороны), где полный min_shared_games (обычно 3) был бы слишком
        # строг — но 1 совместная игра точно так же остаётся шумом, как и
        # для общих напарников/соперников выше. MIN_DUO_GAMES — отдельный,
        # более мягкий порог именно для этих узких событий.
        MIN_DUO_GAMES = 2
        mafia_candidates = [e for e in entries if e["mafia_duo_games"] >= MIN_DUO_GAMES]
        mafia_duo = max(mafia_candidates, key=lambda e: e["mafia_duo_games"], default=None)
        if mafia_duo:
            mafia_duo = {
                **mafia_duo,
                "duo_win_rate": round(mafia_duo["mafia_duo_wins"] / mafia_duo["mafia_duo_games"] * 100, 1),
            }

        # Sheriff vs Don: показываем ту сторону, где у игрока реально есть игры
        sheriff_candidates = [e for e in entries if e["sheriff_vs_don_games"] >= MIN_DUO_GAMES]
        don_candidates = [e for e in entries if e["don_vs_sheriff_games"] >= MIN_DUO_GAMES]
        sheriff_vs_don = None
        if sheriff_candidates:
            best = max(sheriff_candidates, key=lambda e: e["sheriff_vs_don_games"])
            sheriff_vs_don = {
                "as_role": "sheriff", "opponent": best["display_name"], "player_id": best["player_id"],
                "games": best["sheriff_vs_don_games"],
                "win_rate": round(best["sheriff_vs_don_wins"] / best["sheriff_vs_don_games"] * 100, 1),
            }
        elif don_candidates:
            best = max(don_candidates, key=lambda e: e["don_vs_sheriff_games"])
            sheriff_vs_don = {
                "as_role": "don", "opponent": best["display_name"], "player_id": best["player_id"],
                "games": best["don_vs_sheriff_games"],
                "win_rate": round(best["don_vs_sheriff_wins"] / best["don_vs_sheriff_games"] * 100, 1),
            }

        return {
            "nemesis": nemesis,
            "favorite_victim": favorite_victim,
            "best_teammate_wr": best_teammate_wr,
            "worst_teammate_wr": worst_teammate_wr,
            "mafia_duo": mafia_duo,
            "sheriff_vs_don": sheriff_vs_don,
            "most_played_against": most_played_against,
            "min_shared_games": min_shared_games,
        }

    @staticmethod
    def get_tournament_summary(player_id: int) -> dict:
        """
        Loops the player's own finished tournaments (club-scale = dozens)
        calling RatingService.get_tournament_rating() per tournament — cost
        is bounded by participant count per tournament, not total games.
        Future caching target if tournament volume grows significantly.
        """
        from app.models import TournamentParticipant, Tournament
        from app.services.rating_service import RatingService

        participations = (
            db.session.query(TournamentParticipant)
            .join(Tournament)
            .filter(TournamentParticipant.player_id == player_id, Tournament.status == "finished")
            .all()
        )

        finals = sum(1 for p in participations if p.advanced_to_final)
        wins = 0
        podiums = 0
        best_rank = None

        for p in participations:
            ratings = RatingService.get_tournament_rating(p.tournament_id)
            entry = next((r for r in ratings if r.player_id == player_id), None)
            if not entry or not entry.rank:
                continue
            if best_rank is None or entry.rank < best_rank:
                best_rank = entry.rank
            if entry.rank == 1:
                wins += 1
            if entry.rank <= 3:
                podiums += 1

        return {
            "tournament_count": len(participations),
            "best_result": best_rank,
            "finals_count": finals,
            "wins": wins,
            "podiums": podiums,
        }

    @staticmethod
    def get_fantasy_summary(player_id: int) -> Optional[dict]:
        """None immediately if this player has no linked User account —
        Fantasy is keyed by User.id, not Player.id."""
        player = db.session.get(Player, player_id)
        if not player or not player.user:
            return None

        from app.models import FantasyDraft
        from app.services.fantasy_service import FantasyService

        drafts = db.session.query(FantasyDraft).filter_by(user_id=player.user.id).all()
        if not drafts:
            return {"draft_count": 0, "best_draft_points": 0.0, "average_rank": None, "total_points": 0.0}

        total_points = sum(d.total_points for d in drafts)
        best_draft = max(drafts, key=lambda d: d.total_points, default=None)

        ranks = []
        for d in drafts:
            leaderboard = FantasyService.get_leaderboard(d.tournament_id)
            entry = next((e for e in leaderboard if e.user_id == player.user.id), None)
            if entry:
                ranks.append(entry.rank)
        average_rank = round(sum(ranks) / len(ranks), 1) if ranks else None

        return {
            "draft_count": len(drafts),
            "best_draft_points": best_draft.total_points if best_draft else 0.0,
            "average_rank": average_rank,
            "total_points": round(total_points, 2),
        }

    # ── Inventory / Achievements / Customization (delegates) ────────────────────

    @staticmethod
    def get_inventory(player_id: int):
        from app.services.shop_service import ShopService
        return ShopService.get_inventory(player_id)

    @staticmethod
    def get_achievements(player_id: int) -> List[dict]:
        from app.services.achievement_service import AchievementService
        return AchievementService.get_all_with_unlock_status(player_id)

    @staticmethod
    def get_profile_customization(player_id: int) -> dict:
        """Read-only view of currently equipped items, by slot."""
        from app.services.shop_service import ShopService
        equipped = ShopService.get_equipped(player_id)
        return {
            slot: {"inventory_item_id": inv.id, "item": inv.item.to_dict()}
            for slot, inv in equipped.items()
        }
