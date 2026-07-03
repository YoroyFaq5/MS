"""
Migration model
================
Отдельная модель для одноразового Migration API (перенос данных из старой
версии приложения) — вынесена в свой файл по тому же принципу, что и
User в user.py: отдельная забота, отдельный файл, импортируется в
models/__init__.py.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint

from app import db


class LegacyImportMap(db.Model):
    """
    Карта «старый id → новый id» по каждой перенесённой сущности.

    Единственная цель — идемпотентность Migration API: перед созданием
    записи проверяем, не импортирована ли она уже (по entity_type +
    legacy_id), и постоянный аудиторский след для будущей сверки/саппорта.
    Не связана ни с одной бизнес-моделью через ForeignKey намеренно —
    легаси-идентификаторы принадлежат чужой схеме, а не текущей.
    """
    __tablename__ = "legacy_import_map"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(20), nullable=False)   # "player" | "user" | "game" | "gg"
    legacy_id = Column(Integer, nullable=False)
    new_id = Column(Integer, nullable=False)
    imported_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "legacy_id", name="uq_legacy_import"),
    )

    def __repr__(self) -> str:
        return f"<LegacyImportMap {self.entity_type}#{self.legacy_id} -> {self.new_id}>"
