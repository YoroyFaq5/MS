"""
AdminShopService
================
Admin-only CRUD for ShopItem + admin gifting of items to players.
No purchase/equip logic here — that's ShopService's job.
"""
from __future__ import annotations

import logging
from typing import Optional

from app import db
from app.models import Player, ShopItem, InventoryItem, ShopCategory, Rarity
from app.services.shop_service import ShopResult

logger = logging.getLogger(__name__)


class AdminShopService:

    # ── CRUD ─────────────────────────────────────────────────────────────────

    @staticmethod
    def create_item(
        name: str,
        category: ShopCategory,
        subcategory: str,
        price: float,
        description: str = "",
        rarity: Rarity = Rarity.COMMON,
        image_url: Optional[str] = None,
        is_unique_purchase: bool = True,
        data: Optional[dict] = None,
    ) -> ShopResult:
        if not name or not name.strip():
            return ShopResult.fail("Название товара обязательно.")
        if not subcategory or not subcategory.strip():
            return ShopResult.fail("Подкатегория (слот) обязательна.")
        if price <= 0:
            return ShopResult.fail("Цена должна быть положительной.")

        item = ShopItem(
            name=name.strip(),
            description=(description or "").strip() or None,
            category=category,
            subcategory=subcategory.strip(),
            rarity=rarity,
            price=round(float(price), 2),
            image_url=(image_url or "").strip() or None,
            is_unique_purchase=is_unique_purchase,
        )
        item.data = data or {}
        db.session.add(item)
        db.session.commit()
        logger.info(f"Admin created ShopItem #{item.id}: {item.name}")
        return ShopResult.success(f"Товар «{item.name}» создан.", data=item)

    @staticmethod
    def update_item(item_id: int, **fields) -> ShopResult:
        item = db.session.get(ShopItem, item_id)
        if not item:
            return ShopResult.fail("Товар не найден.")

        if "name" in fields and fields["name"] is not None:
            name = fields["name"].strip()
            if not name:
                return ShopResult.fail("Название не может быть пустым.")
            item.name = name

        if "description" in fields and fields["description"] is not None:
            item.description = fields["description"].strip() or None

        if "category" in fields and fields["category"] is not None:
            item.category = fields["category"]

        if "subcategory" in fields and fields["subcategory"] is not None:
            subcat = fields["subcategory"].strip()
            if not subcat:
                return ShopResult.fail("Подкатегория не может быть пустой.")
            item.subcategory = subcat

        if "rarity" in fields and fields["rarity"] is not None:
            item.rarity = fields["rarity"]

        if "price" in fields and fields["price"] is not None:
            if fields["price"] <= 0:
                return ShopResult.fail("Цена должна быть положительной.")
            item.price = round(float(fields["price"]), 2)

        if "image_url" in fields and fields["image_url"] is not None:
            item.image_url = fields["image_url"].strip() or None

        if "is_unique_purchase" in fields and fields["is_unique_purchase"] is not None:
            item.is_unique_purchase = bool(fields["is_unique_purchase"])

        if "is_active" in fields and fields["is_active"] is not None:
            item.is_active = bool(fields["is_active"])

        if "data" in fields and fields["data"] is not None:
            item.data = fields["data"]

        db.session.commit()
        return ShopResult.success(f"Товар «{item.name}» обновлён.", data=item)

    @staticmethod
    def deactivate_item(item_id: int) -> ShopResult:
        """Soft delete — existing InventoryItem rows stay intact/owned."""
        item = db.session.get(ShopItem, item_id)
        if not item:
            return ShopResult.fail("Товар не найден.")
        item.is_active = False
        db.session.commit()
        return ShopResult.success(f"Товар «{item.name}» отключён.", data=item)

    @staticmethod
    def activate_item(item_id: int) -> ShopResult:
        item = db.session.get(ShopItem, item_id)
        if not item:
            return ShopResult.fail("Товар не найден.")
        item.is_active = True
        db.session.commit()
        return ShopResult.success(f"Товар «{item.name}» снова активен.", data=item)

    # ── Admin gifting ────────────────────────────────────────────────────────

    @staticmethod
    def grant_item(player_id: int, item_id: int, reason: str) -> ShopResult:
        """Admin gift — bypasses coin spending. Still respects
        is_unique_purchase unless the item allows repeats (e.g. PHYSICAL)."""
        player = db.session.get(Player, player_id)
        if not player:
            return ShopResult.fail("Игрок не найден.")
        item = db.session.get(ShopItem, item_id)
        if not item:
            return ShopResult.fail("Товар не найден.")
        if not reason or len(reason.strip()) < 3:
            return ShopResult.fail("Укажите причину выдачи.")

        if item.is_unique_purchase:
            owned = (
                db.session.query(InventoryItem)
                .filter_by(player_id=player.id, item_id=item.id)
                .first()
            )
            if owned:
                return ShopResult.fail(f"«{player.display_name}» уже владеет «{item.name}».")

        inv = InventoryItem(
            player_id=player.id,
            item_id=item.id,
            price_paid=0.0,
            source="admin_grant",
        )
        db.session.add(inv)
        db.session.commit()
        logger.info(f"Admin granted ShopItem #{item.id} to player #{player.id}: {reason}")
        return ShopResult.success(
            f"«{item.name}» выдан игроку «{player.display_name}».", data=inv
        )
