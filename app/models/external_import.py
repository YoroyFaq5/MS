"""
External game import models
============================
Отдельная забота — интеграции с внешними сервисами (сейчас: MafiaSpace),
вынесена в свой файл по тому же принципу, что User в user.py и
LegacyImportMap в migration.py.

ExternalPlayerLink — постоянное сопоставление "игрок во внешней системе"
→ "наш Player". Заполняется один раз (автоматически при совпадении ника,
либо вручную админом через /admin/imports), дальше все следующие игры от
того же внешнего игрока находят его сразу.

ExternalGameImport — карточка одного входящего вебхука. external_id —
ключ идемпотентности (тот же external_id повторно не создаёт вторую
игру). status="pending_review" пока хотя бы один игрок не сопоставлен;
raw_payload хранит исходный JSON, чтобы можно было досопоставить игроков
и досоздать игру позже, не запрашивая вебхук заново.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app import db


class ExternalPlayerLink(db.Model):
    __tablename__ = "external_player_links"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    source = Column(String(32), nullable=False)          # "mafiaspace"
    external_id = Column(String(120), nullable=False)     # их id игрока
    nickname_hint = Column(String(80), nullable=True)     # последний известный ник, для отображения
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)

    player = relationship("Player")

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_external_player_link"),
    )

    def __repr__(self) -> str:
        return f"<ExternalPlayerLink {self.source}:{self.external_id} -> player#{self.player_id}>"


class ExternalGameImport(db.Model):
    __tablename__ = "external_game_imports"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    source = Column(String(32), nullable=False)
    external_id = Column(String(120), nullable=False)
    raw_payload = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending_review")  # pending_review | imported | rejected
    game_id = Column(Integer, ForeignKey("games.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    game = relationship("Game")
    revisions = relationship(
        "ExternalGameImportRevision", back_populates="import_row",
        order_by="ExternalGameImportRevision.received_at", cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_external_game_import"),
    )

    def __repr__(self) -> str:
        return f"<ExternalGameImport {self.source}:{self.external_id} status={self.status}>"


class ExternalGameImportRevision(db.Model):
    """
    Одна запись = один реально полученный вебхук по этому external_id —
    и самый первый, и каждый последующий "исправленный протокол". В
    отличие от ExternalGameImport.raw_payload (который всегда хранит
    только ПОСЛЕДНЮЮ версию для удобства повторной обработки), это —
    неизменяемый журнал: что именно и когда пришло, и что изменилось
    по сравнению с предыдущей версией (см.
    ExternalGameImportService._diff_summary).
    """
    __tablename__ = "external_game_import_revisions"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    import_id = Column(Integer, ForeignKey("external_game_imports.id", ondelete="CASCADE"), nullable=False)
    raw_payload = Column(Text, nullable=False)
    summary = Column(String(500), nullable=True)  # человекочитаемый диф с предыдущей версией
    received_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False,
    )

    import_row = relationship("ExternalGameImport", back_populates="revisions")

    def __repr__(self) -> str:
        return f"<ExternalGameImportRevision import#{self.import_id} at={self.received_at}>"
