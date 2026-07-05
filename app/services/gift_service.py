"""
GiftService
===========
Передача предметов инвентаря между игроками. Передача мгновенная — без
pending/accept-состояния (см. модель GiftTransfer): владение InventoryItem
меняется сразу, а "уведомление" — это просто счётчик непрочитанных записей
GiftTransfer, читаемый при обычной загрузке страницы (как #nav-coins в
base.html), без websocket.

Не трогает монеты — это чистая передача владения, EconomyService здесь не
нужен.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import or_

from app import db
from app.models import Player, InventoryItem, GiftTransfer

logger = logging.getLogger(__name__)


@dataclass
class GiftResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "GiftResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "GiftResult":
        return cls(ok=False, message=msg)


class GiftService:

    # ── Отправка подарка ──────────────────────────────────────────────────────

    @staticmethod
    def send_gift(
        sender: Player,
        inventory_item_id: int,
        to_player_id: int,
        message: Optional[str] = None,
    ) -> GiftResult:
        inv = db.session.get(InventoryItem, inventory_item_id)
        if not inv or inv.player_id != sender.id:
            return GiftResult.fail("Предмет не найден в вашем инвентаре.")

        item = inv.item
        if inv.is_equipped:
            return GiftResult.fail("Нельзя подарить экипированный предмет — сначала снимите его.")
        if not item.is_transferable:
            return GiftResult.fail(f"«{item.name}» нельзя передавать другим игрокам.")

        if to_player_id == sender.id:
            return GiftResult.fail("Нельзя подарить предмет самому себе.")
        recipient = db.session.get(Player, to_player_id)
        if not recipient or not recipient.is_active:
            return GiftResult.fail("Получатель не найден или неактивен.")

        message = (message or "").strip() or None
        if message and not item.giftable_message:
            return GiftResult.fail(f"К подарку «{item.name}» нельзя приложить сообщение.")

        inv.player_id = to_player_id
        inv.is_equipped = False
        inv.source = "gift"

        transfer = GiftTransfer(
            inventory_item_id=inv.id,
            shop_item_id=item.id,
            from_player_id=sender.id,
            to_player_id=to_player_id,
            message=message,
        )
        db.session.add(transfer)
        db.session.commit()

        logger.info(f"Gift: player#{sender.id} -> player#{to_player_id}, item={item.name!r}")

        from app.services.bot_notify_service import BotNotifyService
        BotNotifyService.notify_player(
            to_player_id, "gift-received",
            {"item_name": item.name, "sender_name": sender.display_name, "message": message},
        )

        return GiftResult.success(
            f"«{item.name}» подарен игроку «{recipient.display_name}».", data=transfer
        )

    # ── Чтение ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_incoming_gifts(player_id: int, unseen_only: bool = False) -> List[GiftTransfer]:
        q = db.session.query(GiftTransfer).filter_by(to_player_id=player_id)
        if unseen_only:
            q = q.filter_by(seen=False)
        return q.order_by(GiftTransfer.transferred_at.desc()).all()

    @staticmethod
    def get_transfer_history(player_id: int, limit: int = 50) -> List[GiftTransfer]:
        return (
            db.session.query(GiftTransfer)
            .filter(or_(GiftTransfer.from_player_id == player_id, GiftTransfer.to_player_id == player_id))
            .order_by(GiftTransfer.transferred_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def mark_seen(player_id: int) -> None:
        db.session.query(GiftTransfer).filter_by(to_player_id=player_id, seen=False).update({"seen": True})
        db.session.commit()

    @staticmethod
    def get_unseen_count(player_id: int) -> int:
        return (
            db.session.query(GiftTransfer)
            .filter_by(to_player_id=player_id, seen=False)
            .count()
        )

    # ── Админ: обзор всех передач ────────────────────────────────────────────

    @staticmethod
    def get_all_transfers(limit: int = 100, offset: int = 0) -> List[GiftTransfer]:
        """Отдельный от get_transfer_history метод — тот намеренно ограничен
        одним игроком, здесь — полный обзор для админ-панели."""
        return (
            db.session.query(GiftTransfer)
            .order_by(GiftTransfer.transferred_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
