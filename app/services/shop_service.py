"""
ShopService
===========
Purchasing, ownership and equip/unequip logic for the coin-economy shop.

Equip model: a ShopItem's (category, subcategory) pair defines an equip
"slot". A player may have at most one equipped InventoryItem per slot —
equipping a new item in a slot auto-unequips whatever else occupied it.
This is entirely data-driven off those two columns, so new subcategories
(new cosmetic slots) never require code changes here (Open/Closed).

PHYSICAL items are never equippable — purchasing them only spends coins;
fulfillment happens manually by an admin outside the app.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from app import db
from app.models import Player, ShopItem, InventoryItem, ShopCategory, Rarity, CoinSourceType
from app.services.economy_service import EconomyService

logger = logging.getLogger(__name__)

# Mythic/Ultra — не "макс. 1 на игрока" (как обычный is_unique_purchase),
# а ровно 1 экземпляр на весь клуб. Как только кто-то владеет им, его
# больше нельзя купить обычной покупкой — только перекупить дороже через
# buyout_item(). Прежний владелец получает часть суммы перекупа (не всю —
# комиссия клуба), остальное сгорает, как и при обычной покупке.
UNIQUE_RARITIES = {Rarity.MYTHIC, Rarity.ULTRA}
MIN_BUYOUT_INCREMENT = 100.0
RESALE_OWNER_SHARE = 0.8


@dataclass
class ShopResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "ShopResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "ShopResult":
        return cls(ok=False, message=msg)


class ShopService:

    # ── Browsing ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_items(category: Optional[ShopCategory] = None, active_only: bool = True) -> List[ShopItem]:
        q = db.session.query(ShopItem)
        if active_only:
            q = q.filter(ShopItem.is_active == True)
        if category is not None:
            q = q.filter(ShopItem.category == category)
        return q.order_by(ShopItem.category, ShopItem.subcategory, ShopItem.price).all()

    @staticmethod
    def get_item(item_id: int) -> Optional[ShopItem]:
        return db.session.get(ShopItem, item_id)

    # ── Purchase ─────────────────────────────────────────────────────────────

    @staticmethod
    def purchase(player: Player, item_id: int) -> ShopResult:
        item = db.session.get(ShopItem, item_id)
        if not item or not item.is_active:
            return ShopResult.fail("Товар не найден или недоступен.")

        if item.is_unique_purchase:
            owned = (
                db.session.query(InventoryItem)
                .filter_by(player_id=player.id, item_id=item.id)
                .first()
            )
            if owned:
                return ShopResult.fail(f"«{item.name}» уже куплен.")

        econ_result = EconomyService.spend_coins(
            player, item.price, f"Покупка: {item.name}", commit=False
        )
        if not econ_result.ok:
            return ShopResult.fail(econ_result.message)

        inv = InventoryItem(
            player_id=player.id,
            item_id=item.id,
            price_paid=item.price,
            source="purchase",
        )
        db.session.add(inv)
        db.session.commit()
        logger.info(f"Player #{player.id} purchased ShopItem #{item.id} ({item.name})")

        try:
            from app.services.achievement_service import AchievementService
            AchievementService.check_after_purchase(player.id)
        except Exception:
            logger.exception(f"Achievement check failed after purchase for player #{player.id}")

        return ShopResult.success(f"«{item.name}» куплен за {item.price:.0f} монет.", data=inv)

    # ── Inventory ────────────────────────────────────────────────────────────

    @staticmethod
    def get_inventory(player_id: int, category: Optional[ShopCategory] = None) -> List[InventoryItem]:
        q = (
            db.session.query(InventoryItem)
            .join(ShopItem)
            .filter(InventoryItem.player_id == player_id)
        )
        if category is not None:
            q = q.filter(ShopItem.category == category)
        return q.order_by(ShopItem.category, ShopItem.subcategory, InventoryItem.acquired_at.desc()).all()

    @staticmethod
    def get_equipped(player_id: int) -> Dict[str, InventoryItem]:
        """One query. Returns {'category:subcategory': InventoryItem, ...}."""
        rows = (
            db.session.query(InventoryItem)
            .join(ShopItem)
            .filter(InventoryItem.player_id == player_id, InventoryItem.is_equipped == True)
            .all()
        )
        return {inv.item.slot_key: inv for inv in rows}

    @staticmethod
    def get_equipped_bulk(player_ids: List[int]) -> Dict[int, Dict[str, InventoryItem]]:
        """
        Batched get_equipped() for many players at once — one query instead
        of N. Used when rendering a list of player names (leaderboards,
        game rosters, tournament pages, …) so personalization doesn't turn
        into an N+1 query storm.
        Returns {player_id: {'category:subcategory': InventoryItem, ...}, ...}
        — every requested player_id is present as a key, even with an empty
        dict, so callers can safely do `.get(pid, {})`.
        """
        result: Dict[int, Dict[str, InventoryItem]] = {pid: {} for pid in player_ids}
        if not player_ids:
            return result
        rows = (
            db.session.query(InventoryItem)
            .join(ShopItem)
            .filter(InventoryItem.player_id.in_(player_ids), InventoryItem.is_equipped == True)
            .all()
        )
        for inv in rows:
            result[inv.player_id][inv.item.slot_key] = inv
        return result

    # ── Equip / Unequip ──────────────────────────────────────────────────────

    @staticmethod
    def equip_item(player: Player, inventory_item_id: int) -> ShopResult:
        inv = db.session.get(InventoryItem, inventory_item_id)
        if not inv or inv.player_id != player.id:
            return ShopResult.fail("Предмет не найден в инвентаре.")

        item = inv.item
        if item.category == ShopCategory.PHYSICAL:
            return ShopResult.fail("Этот предмет нельзя надеть — это физический товар.")

        # Unequip any other item occupying the same slot for this player.
        others = (
            db.session.query(InventoryItem)
            .join(ShopItem)
            .filter(
                InventoryItem.player_id == player.id,
                InventoryItem.is_equipped == True,
                InventoryItem.id != inv.id,
                ShopItem.category == item.category,
                ShopItem.subcategory == item.subcategory,
            )
            .all()
        )
        for other in others:
            other.is_equipped = False

        inv.is_equipped = True
        db.session.commit()
        return ShopResult.success(f"«{item.name}» экипирован.", data=inv)

    @staticmethod
    def unequip_item(player: Player, inventory_item_id: int) -> ShopResult:
        inv = db.session.get(InventoryItem, inventory_item_id)
        if not inv or inv.player_id != player.id:
            return ShopResult.fail("Предмет не найден в инвентаре.")

        inv.is_equipped = False
        db.session.commit()
        return ShopResult.success(f"«{inv.item.name}» снят.", data=inv)

    # ── Validation helper ────────────────────────────────────────────────────

    @staticmethod
    def validate_purchase(player: Player, item: ShopItem) -> ShopResult:
        """Standalone pre-check (no side effects) — used by templates/routes
        to show whether a purchase button should be enabled."""
        if not item.is_active:
            return ShopResult.fail("Товар недоступен.")
        if item.is_unique_purchase:
            owned = (
                db.session.query(InventoryItem)
                .filter_by(player_id=player.id, item_id=item.id)
                .first()
            )
            if owned:
                return ShopResult.fail("Уже куплено.")
        if not EconomyService.validate_balance(player, item.price):
            return ShopResult.fail("Недостаточно монет.")
        return ShopResult.success("OK")
