"""
TitleService
============
Хранение и управление титулами игрока: выдача, отзыв, экипировка.

Формулы начисления титулов (сезонные номинации, "вечные" рекорды клуба)
живут отдельно, в NominationService — этот сервис отвечает только за
хранение факта награды и состояние экипировки, по аналогии с тем, как
ShopService отделён от логики покупки/скидок.

В один момент времени у игрока может быть экипирован только один титул
(в отличие от ShopItem, где слотов много) — экипировка нового титула
снимает предыдущий.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from app import db
from app.models import Player, Title, PlayerTitle, TitleType

logger = logging.getLogger(__name__)


@dataclass
class TitleResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "TitleResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "TitleResult":
        return cls(ok=False, message=msg)


class TitleService:

    # ── Визуальная категория ("флейвор") титула ──────────────────────────────
    # Title не хранит category (в отличие от Achievement) — набор титулов
    # маленький и курируемый (см. коды в nomination_service.py), поэтому
    # проще держать явное сопоставление здесь, чем гонять миграцию ради
    # decorative-поля. Неизвестный код (ручной админский титул) получает
    # "special" — нейтральный фолбэк, а не падение/пустой цвет.
    _TITLE_FLAVORS: Dict[str, str] = {
        "club_legend":           "special",     # лучший общий перформанс
        "streak_king":           "streak",      # победная серия
        "iron_player":           "special",     # больше всех игр
        "mafia_terror":          "defense",     # лучший WR за город
        "dark_genius":           "intellect",   # лучший WR за мафию — хитрость
        "season_best_civilian":  "defense",
        "season_best_sheriff":   "intellect",   # детектив — расследование
        "season_best_mafia":     "aggression",
        "season_best_don":       "aggression",
    }

    FLAVOR_LABELS: Dict[str, str] = {
        "defense":    "Защита",
        "intellect":  "Интеллект",
        "streak":     "Серия побед",
        "rating":     "Рейтинг",
        "aggression": "Агрессия",
        "special":    "Особый",
    }

    @staticmethod
    def get_title_flavor(code: str) -> str:
        return TitleService._TITLE_FLAVORS.get(code, "special")

    # Порядок редкости для сортировки "самые значимые — сверху" (Rarity
    # enum сам по себе не упорядочен по значимости — тут явный порядок).
    RARITY_RANK: Dict[str, int] = {
        "common": 0, "rare": 1, "epic": 2, "legendary": 3, "mythic": 4, "ultra": 5,
    }

    # ── Чтение (используется в профиле/хедере/лидербордах) ───────────────────

    @staticmethod
    def get_equipped_title(player_id: int) -> Optional[PlayerTitle]:
        """Один запрос — дешёвое чтение для отображения титула рядом с ником."""
        return (
            db.session.query(PlayerTitle)
            .filter_by(player_id=player_id, equipped=True, revoked=False)
            .first()
        )

    @staticmethod
    def get_equipped_titles_bulk(player_ids: List[int]) -> Dict[int, PlayerTitle]:
        """
        Один запрос `IN (...)` для списка игроков — используется в лидербордах,
        чтобы показ титулов не превращался в N+1.
        """
        if not player_ids:
            return {}
        rows = (
            db.session.query(PlayerTitle)
            .filter(
                PlayerTitle.player_id.in_(player_ids),
                PlayerTitle.equipped == True,
                PlayerTitle.revoked == False,
            )
            .all()
        )
        return {row.player_id: row for row in rows}

    @staticmethod
    def list_player_titles(player_id: int) -> List[PlayerTitle]:
        """Полная история наград (включая отозванные) — для прозрачности."""
        return (
            db.session.query(PlayerTitle)
            .filter_by(player_id=player_id)
            .order_by(PlayerTitle.awarded_at.desc())
            .all()
        )

    @staticmethod
    def get_current_global_holders() -> List[PlayerTitle]:
        """Текущие обладатели ETERNAL-титулов (для главной страницы/страницы номинаций)."""
        return (
            db.session.query(PlayerTitle)
            .join(Title)
            .filter(Title.type == TitleType.ETERNAL, PlayerTitle.revoked == False)
            .all()
        )

    @staticmethod
    def get_season_nominations(season_id: int) -> List[PlayerTitle]:
        """Все сезонные награды конкретного сезона (для блока «Номинации сезона»)."""
        return (
            db.session.query(PlayerTitle)
            .filter_by(season_id=season_id, revoked=False)
            .all()
        )

    @staticmethod
    def get_seasonal_history() -> List[dict]:
        """
        Все сезонные награды всех сезонов, сгруппированные по сезону
        (новые сезоны первыми) — для истории на странице номинаций.
        """
        from app.models import Season

        rows = (
            db.session.query(PlayerTitle)
            .join(Title)
            .filter(Title.type == TitleType.SEASONAL, PlayerTitle.revoked == False)
            .all()
        )
        by_season: Dict[int, List[PlayerTitle]] = {}
        for pt in rows:
            by_season.setdefault(pt.season_id, []).append(pt)

        seasons = {
            s.id: s for s in db.session.query(Season).filter(Season.id.in_(by_season.keys())).all()
        } if by_season else {}

        history = [
            {"season": seasons[sid].to_dict(), "awards": [pt.to_dict() for pt in awards]}
            for sid, awards in by_season.items() if sid in seasons
        ]
        history.sort(key=lambda h: (h["season"]["year"], h["season"]["number"]), reverse=True)
        return history

    # ── Экипировка ────────────────────────────────────────────────────────────

    @staticmethod
    def equip(player: Player, player_title_id: int) -> TitleResult:
        pt = db.session.get(PlayerTitle, player_title_id)
        if not pt or pt.player_id != player.id:
            return TitleResult.fail("Титул не найден.")
        if pt.revoked:
            return TitleResult.fail("Этот титул был отозван и не может быть экипирован.")

        # Снимаем любой другой экипированный титул этого игрока — экипирован
        # может быть только один титул одновременно.
        db.session.query(PlayerTitle).filter(
            PlayerTitle.player_id == player.id,
            PlayerTitle.id != pt.id,
            PlayerTitle.equipped == True,
        ).update({"equipped": False})

        pt.equipped = True
        db.session.commit()
        return TitleResult.success(f"Титул «{pt.title.name}» экипирован.", data=pt)

    @staticmethod
    def unequip(player: Player) -> TitleResult:
        pt = TitleService.get_equipped_title(player.id)
        if not pt:
            return TitleResult.success("Нет экипированного титула.")
        pt.equipped = False
        db.session.commit()
        return TitleResult.success("Титул снят.")

    # ── Выдача ───────────────────────────────────────────────────────────────

    @staticmethod
    def grant_title(
        player_id: int,
        title_code: str,
        season_id: Optional[int] = None,
        granted_by: str = "system",
        admin_id: Optional[int] = None,
        reason: Optional[str] = None,
        commit: bool = True,
    ) -> TitleResult:
        title = db.session.query(Title).filter_by(code=title_code, is_active=True).first()
        if not title:
            return TitleResult.fail(f"Титул с кодом «{title_code}» не найден или неактивен.")

        # Дедупликация: один и тот же титул за один и тот же сезон не выдаётся
        # игроку повторно (для ETERNAL/MANUAL — season_id всегда None, поэтому
        # проверка одинаково защищает оба случая).
        exists = (
            db.session.query(PlayerTitle)
            .filter_by(player_id=player_id, title_id=title.id, season_id=season_id, revoked=False)
            .first()
        )
        if exists:
            return TitleResult.success("Титул уже выдан ранее.", data=exists)

        if granted_by == "admin" and not (reason and reason.strip()):
            return TitleResult.fail("Для ручной выдачи титула укажите причину.")

        pt = PlayerTitle(
            player_id=player_id,
            title_id=title.id,
            season_id=season_id,
            granted_by=granted_by,
            admin_id=admin_id,
            reason=reason.strip() if reason else None,
        )
        db.session.add(pt)
        if commit:
            db.session.commit()

        logger.info(f"Title granted: player#{player_id} title={title_code!r} season={season_id} by={granted_by}")

        from app.services.bot_notify_service import BotNotifyService
        BotNotifyService.notify_player(
            player_id, "title-granted", {"title_name": title.name, "title_code": title.code},
        )

        return TitleResult.success(f"Титул «{title.name}» выдан.", data=pt)

    @staticmethod
    def revoke_current_holder_if_any(title_code: str, commit: bool = True) -> None:
        """
        Используется NominationService при пересчёте "вечных" титулов: если у
        титула уже есть текущий обладатель, отзывает его награду (и снимает
        экипировку, если титул был надет) перед выдачей новому рекордсмену.
        """
        title = db.session.query(Title).filter_by(code=title_code).first()
        if not title:
            return
        current = (
            db.session.query(PlayerTitle)
            .filter_by(title_id=title.id, revoked=False)
            .first()
        )
        if not current:
            return
        current.revoked = True
        current.equipped = False
        if commit:
            db.session.commit()

    # ── Админ ────────────────────────────────────────────────────────────────

    @staticmethod
    def admin_grant(admin_user, player_id: int, title_code: str, reason: str) -> TitleResult:
        return TitleService.grant_title(
            player_id=player_id,
            title_code=title_code,
            granted_by="admin",
            admin_id=admin_user.id,
            reason=reason,
        )

    @staticmethod
    def admin_revoke(player_title_id: int) -> TitleResult:
        pt = db.session.get(PlayerTitle, player_title_id)
        if not pt:
            return TitleResult.fail("Награда не найдена.")
        if pt.revoked:
            return TitleResult.fail("Титул уже был отозван.")
        pt.revoked = True
        pt.equipped = False
        db.session.commit()
        return TitleResult.success(f"Титул «{pt.title.name}» отозван у «{pt.player.display_name}».", data=pt)
