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

# Rarity is a plain PyEnum (string values), so ORDER BY on the column would
# sort alphabetically, not COMMON→ULTRA. This maps each member to its
# declaration-order rank for use as a Python-side sort key.
RARITY_ORDER: Dict[Rarity, int] = {r: i for i, r in enumerate(Rarity)}


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
    def list_items(
        category: Optional[ShopCategory] = None,
        active_only: bool = True,
        sort: Optional[str] = None,
    ) -> List[ShopItem]:
        q = db.session.query(ShopItem)
        if active_only:
            q = q.filter(ShopItem.is_active == True)
        if category is not None:
            q = q.filter(ShopItem.category == category)
        items = q.order_by(ShopItem.category, ShopItem.subcategory, ShopItem.price).all()

        if sort == "rarity_desc":
            items.sort(key=lambda i: RARITY_ORDER[i.rarity], reverse=True)
        elif sort == "rarity_asc":
            items.sort(key=lambda i: RARITY_ORDER[i.rarity])
        return items

    @staticmethod
    def get_item(item_id: int) -> Optional[ShopItem]:
        return db.session.get(ShopItem, item_id)

    # ── Purchase ─────────────────────────────────────────────────────────────

    @staticmethod
    def purchase(player: Player, item_id: int) -> ShopResult:
        item = db.session.get(ShopItem, item_id)
        if not item or not item.is_active:
            return ShopResult.fail("Товар не найден или недоступен.")

        if item.rarity in UNIQUE_RARITIES:
            existing = ShopService.get_current_owner(item.id)
            if existing:
                if existing.player_id == player.id:
                    return ShopResult.fail(f"«{item.name}» уже у вас.")
                min_offer = existing.price_paid + MIN_BUYOUT_INCREMENT
                return ShopResult.fail(
                    f"«{item.name}» уже принадлежит другому игроку. "
                    f"Это уникальный предмет — можно только перекупить дороже "
                    f"(мин. {min_offer:.0f} монет)."
                )
        elif item.is_unique_purchase:
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

    # ── Уникальные предметы (Mythic/Ultra) — перекуп ────────────────────────────

    @staticmethod
    def get_current_owner(item_id: int) -> Optional[InventoryItem]:
        """Единственный (по построению) владелец Mythic/Ultra-предмета,
        если он уже куплен — иначе None."""
        return db.session.query(InventoryItem).filter_by(item_id=item_id).first()

    @staticmethod
    def buyout_item(challenger: Player, item_id: int, offer_price: float) -> ShopResult:
        """
        Перекупает уникальный (Mythic/Ultra) предмет у текущего владельца.
        Требует offer_price >= цена_прошлого_владельца + MIN_BUYOUT_INCREMENT.
        Прежний владелец получает RESALE_OWNER_SHARE от offer_price, остаток —
        комиссия клуба (сгорает, как и обычная покупка). Владение переходит
        сразу — старая InventoryItem удаляется (снимая её как экипированную
        автоматически, вместе с записью), новая создаётся для покупателя.
        """
        item = db.session.get(ShopItem, item_id)
        if not item or not item.is_active:
            return ShopResult.fail("Товар не найден или недоступен.")
        if item.rarity not in UNIQUE_RARITIES:
            return ShopResult.fail("Перекуп доступен только для предметов редкости Mythic и Ultra.")

        existing = ShopService.get_current_owner(item.id)
        if not existing:
            return ShopResult.fail("Этот предмет ещё никем не куплен — оформите обычную покупку.")
        if existing.player_id == challenger.id:
            return ShopResult.fail("Вы уже владеете этим предметом.")

        min_offer = existing.price_paid + MIN_BUYOUT_INCREMENT
        if offer_price < min_offer:
            return ShopResult.fail(
                f"Минимальная ставка — {min_offer:.0f} монет "
                f"(текущая цена {existing.price_paid:.0f} + шаг {MIN_BUYOUT_INCREMENT:.0f})."
            )

        spend_result = EconomyService.spend_coins(
            challenger, offer_price, f"Перекуп: {item.name}", commit=False
        )
        if not spend_result.ok:
            return ShopResult.fail(spend_result.message)

        previous_owner = db.session.get(Player, existing.player_id)
        payout = round(offer_price * RESALE_OWNER_SHARE, 2)
        if previous_owner and payout > 0:
            EconomyService.add_coins(
                previous_owner, payout,
                f"«{item.name}» перекуплен игроком {challenger.display_name} за {offer_price:.0f}",
                CoinSourceType.RESALE_PAYOUT, commit=False,
            )

        db.session.delete(existing)
        db.session.flush()

        new_inv = InventoryItem(
            player_id=challenger.id,
            item_id=item.id,
            price_paid=offer_price,
            source="buyout",
        )
        db.session.add(new_inv)
        db.session.commit()
        logger.info(
            f"Player #{challenger.id} bought out ShopItem #{item.id} "
            f"from player #{previous_owner.id if previous_owner else '?'} for {offer_price}"
        )

        if previous_owner:
            from app.services.bot_notify_service import BotNotifyService
            BotNotifyService.notify_player(
                previous_owner.id, "item-bought-out",
                {
                    "item_name": item.name,
                    "buyer_name": challenger.display_name,
                    "offer_price": offer_price,
                    "payout": payout,
                },
            )

        try:
            from app.services.achievement_service import AchievementService
            AchievementService.check_after_purchase(challenger.id)
        except Exception:
            logger.exception(f"Achievement check failed after buyout for player #{challenger.id}")

        return ShopResult.success(
            f"Вы перекупили «{item.name}» за {offer_price:.0f} монет! "
            f"Прежний владелец получил {payout:.0f}.",
            data=new_inv,
        )

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
        if item.rarity in UNIQUE_RARITIES:
            existing = ShopService.get_current_owner(item.id)
            if existing:
                if existing.player_id == player.id:
                    return ShopResult.fail("Уже у вас.")
                return ShopResult.fail("Занято — доступен только перекуп.")
        elif item.is_unique_purchase:
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
