"""
BarService
==========
Real-world bar/shop redemptions — a player shows a short-lived signed QR
from their profile, an admin scans it and charges coins for a physical
item (or a free-form amount) at the counter.

Anti-abuse (see BarRedemption + the route layer in app/routes/bar.py):
- The QR token is signed and time-limited (TOKEN_MAX_AGE_SECONDS) — it
  can't be forged (no player_id/amount to guess or tamper with) and a
  screenshot of it stops working shortly after it's taken.
- The token alone never lets anyone self-charge: only a route protected by
  @admin_required can act on it, so a player (or anyone else) opening
  their own QR link just hits that wall.
- Every redemption/void is attributed to the acting admin (BarRedemption.
  admin_id / voided_by_admin_id). Since anyone who can redeem is already a
  trusted site admin, that attribution — not access restriction — is the
  actual control against staff abuse: it gives the owner a per-admin,
  per-shift trail to reconcile against the register.
- Voids are compensating refund transactions, never edits/deletes — the
  ledger is never silently rewritten, only appended to.
- The real balance check inside EconomyService.spend_coins caps the blast
  radius of any single bad charge at whatever the player actually has.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app import db
from app.models import Player, ShopItem, ShopCategory, BarRedemption, CoinSourceType
from app.services.economy_service import EconomyService

logger = logging.getLogger(__name__)

TOKEN_SALT = "bar-redeem"
TOKEN_MAX_AGE_SECONDS = 300  # 5 minutes


@dataclass
class BarResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "BarResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "BarResult":
        return cls(ok=False, message=msg)


class BarService:

    # ── QR token ─────────────────────────────────────────────────────────
    # Stateless by design — nothing is stored in the DB for an issued
    # token, validity is entirely a function of the signature + timestamp,
    # so there's no new column on Player and no "outstanding tokens" table
    # to clean up.

    @staticmethod
    def _serializer() -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=TOKEN_SALT)

    @staticmethod
    def build_redeem_token(player_id: int) -> str:
        return BarService._serializer().dumps(player_id)

    @staticmethod
    def verify_redeem_token(token: str) -> Optional[int]:
        """Player id the token was issued for, or None if the signature is
        invalid or it's older than TOKEN_MAX_AGE_SECONDS."""
        try:
            return BarService._serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
        except (BadSignature, SignatureExpired):
            return None

    # ── Catalog ──────────────────────────────────────────────────────────

    @staticmethod
    def list_catalog() -> List[ShopItem]:
        return (
            db.session.query(ShopItem)
            .filter(ShopItem.category == ShopCategory.PHYSICAL, ShopItem.is_active == True)
            .order_by(ShopItem.subcategory, ShopItem.price)
            .all()
        )

    # ── Redeem / void ────────────────────────────────────────────────────

    @staticmethod
    def redeem(
        player_id: int,
        admin_id: int,
        item_id: Optional[int] = None,
        custom_amount: Optional[float] = None,
        note: str = "",
    ) -> BarResult:
        player = db.session.get(Player, player_id)
        if not player:
            return BarResult.fail("Игрок не найден.")

        if item_id is not None and custom_amount is not None:
            return BarResult.fail("Укажите либо товар из каталога, либо свою сумму — не оба сразу.")
        if item_id is None and custom_amount is None:
            return BarResult.fail("Укажите товар из каталога или свою сумму.")

        item = None
        if item_id is not None:
            item = db.session.get(ShopItem, item_id)
            if not item or item.category != ShopCategory.PHYSICAL or not item.is_active:
                return BarResult.fail("Товар не найден или недоступен.")
            amount = item.price
            item_name = item.name
            reason = f"Бар: {item.name}"
        else:
            if custom_amount <= 0:
                return BarResult.fail("Сумма должна быть положительной.")
            if len(note.strip()) < 3:
                return BarResult.fail("Для свободной суммы укажите комментарий (что купили).")
            amount = custom_amount
            item_name = None
            reason = f"Бар: {note.strip()}"

        econ_result = EconomyService.spend_coins(player, amount, reason, commit=False)
        if not econ_result.ok:
            return BarResult.fail(econ_result.message)

        redemption = BarRedemption(
            player_id=player.id,
            admin_id=admin_id,
            item_id=item.id if item else None,
            item_name_snapshot=item_name,
            amount=amount,
            note=note.strip() or None,
            coin_transaction=econ_result.data,
        )
        db.session.add(redemption)
        db.session.commit()
        logger.info(
            f"Bar redemption: admin#{admin_id} charged player#{player.id} "
            f"{amount:.2f} coins ({reason})"
        )
        return BarResult.success(
            f"Списано {amount:.0f} монет у {player.display_name}. Остаток: {player.coins:.0f}.",
            data=redemption,
        )

    @staticmethod
    def void(redemption_id: int, admin_id: int, reason: str) -> BarResult:
        redemption = db.session.get(BarRedemption, redemption_id)
        if not redemption:
            return BarResult.fail("Списание не найдено.")
        if redemption.is_voided:
            return BarResult.fail("Это списание уже отменено.")
        if len(reason.strip()) < 5:
            return BarResult.fail("Укажите причину отмены.")

        econ_result = EconomyService.add_coins(
            redemption.player, redemption.amount,
            f"Отмена списания в баре: {reason.strip()}",
            CoinSourceType.ADMIN_ADJUSTMENT, commit=False,
        )
        if not econ_result.ok:
            return BarResult.fail(econ_result.message)

        redemption.voided_at = datetime.now(timezone.utc)
        redemption.voided_by_admin_id = admin_id
        redemption.void_coin_transaction = econ_result.data
        db.session.commit()
        logger.info(f"Bar redemption #{redemption.id} voided by admin#{admin_id}: {reason}")
        return BarResult.success(f"Списание отменено, {redemption.amount:.0f} монет возвращено.")

    # ── Reconciliation log ───────────────────────────────────────────────

    @staticmethod
    def recent(limit: int = 100) -> List[BarRedemption]:
        return (
            db.session.query(BarRedemption)
            .order_by(BarRedemption.created_at.desc())
            .limit(limit)
            .all()
        )
