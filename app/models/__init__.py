from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum as PyEnum
import json

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date,
    ForeignKey, Enum, Text, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, validates

from app import db


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Role(PyEnum):
    CIVILIAN = "civilian"
    MAFIA = "mafia"
    DON = "don"
    SHERIFF = "sheriff"


class WinSide(PyEnum):
    MAFIA = "mafia"
    CITY = "city"
    NONE = "none"


class TournamentType(PyEnum):
    INDIVIDUAL = "individual"
    TEAM = "team"


class StageType(PyEnum):
    GROUP = "group"
    MAIN = "main"
    FINAL = "final"


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player(db.Model):
    __tablename__ = "players"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    nickname = Column(String(80), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    # NOTE: unused legacy column, not a real FK. The actual Player↔User
    # link is User.player_id (see app/models/user.py). Kept here only so
    # existing DB rows/columns aren't touched by a schema change.
    user_id = Column(Integer, nullable=True)

    # ELO rating field (future extension hook)
    elo = Column(Float, default=1000.0, nullable=False)

    # Profile & economy fields (added via migration for existing DBs)
    avatar_url = Column(String(512), nullable=True)
    bio        = Column(Text, nullable=True)
    coins      = Column(Float, default=0.0, nullable=False, server_default="0")

    # Telegram-аккаунт, привязанный через Login Widget (см. AuthService.
    # link_telegram) — используется отдельным Telegram-ботом для резолва
    # "кто это" через API; сам бот эту связь у себя не хранит.
    telegram_id = Column(String(32), nullable=True, unique=True, index=True)

    game_slots = relationship("GameSlot", back_populates="player", lazy="dynamic")
    tournament_participations = relationship("TournamentParticipant", back_populates="player", lazy="dynamic")
    team_memberships = relationship("TeamPlayer", back_populates="player", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Player {self.name!r}>"

    @property
    def display_name(self) -> str:
        return self.nickname or self.name

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "nickname": self.nickname,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "elo": self.elo,
            "created_at": self.created_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Tournament
# ---------------------------------------------------------------------------

class Tournament(db.Model):
    __tablename__ = "tournaments"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(
        Enum(TournamentType, name="tournament_type_enum"),
        nullable=False,
        default=TournamentType.INDIVIDUAL,
    )
    is_ranked = Column(Boolean, default=True, nullable=False)
    has_stages = Column(Boolean, default=False, nullable=False)
    # Cutoff: how many players advance from main→final stage
    cutoff_size = Column(Integer, default=10, nullable=False)

    status = Column(String(20), default="pending", nullable=False)
    # pending → active → finished

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    stages = relationship(
        "TournamentStage", back_populates="tournament",
        cascade="all, delete-orphan", order_by="TournamentStage.order"
    )
    participants = relationship(
        "TournamentParticipant", back_populates="tournament",
        cascade="all, delete-orphan"
    )
    teams = relationship(
        "Team", back_populates="tournament",
        cascade="all, delete-orphan"
    )
    games = relationship("Game", back_populates="tournament", foreign_keys="Game.tournament_id")

    def __repr__(self) -> str:
        return f"<Tournament {self.name!r} [{self.type.value}]>"

    @property
    def active_stage(self):
        """Return the currently active stage (status='active')."""
        for s in self.stages:
            if s.status == "active":
                return s
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "is_ranked": self.is_ranked,
            "has_stages": self.has_stages,
            "cutoff_size": self.cutoff_size,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


# ---------------------------------------------------------------------------
# TournamentStage
# ---------------------------------------------------------------------------

class TournamentStage(db.Model):
    __tablename__ = "tournament_stages"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    tournament_id = Column(
        Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(80), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    type = Column(
        Enum(StageType, name="stage_type_enum"),
        nullable=False,
        default=StageType.MAIN,
    )
    status = Column(String(20), default="pending", nullable=False)
    # pending → active → finished

    tournament = relationship("Tournament", back_populates="stages")
    games = relationship("Game", back_populates="stage", foreign_keys="Game.stage_id")

    __table_args__ = (
        UniqueConstraint("tournament_id", "order", name="uq_stage_order"),
    )

    def __repr__(self) -> str:
        return f"<Stage {self.name!r} [{self.type.value}] order={self.order}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "name": self.name,
            "order": self.order,
            "type": self.type.value,
            "status": self.status,
            "games_count": len(self.games),
        }


# ---------------------------------------------------------------------------
# Team (fixed per tournament)
# ---------------------------------------------------------------------------

class Team(db.Model):
    __tablename__ = "teams"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    tournament_id = Column(
        Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(80), nullable=False)
    color = Column(String(7), nullable=True)  # hex color for UI

    tournament = relationship("Tournament", back_populates="teams")
    members = relationship("TeamPlayer", back_populates="team", cascade="all, delete-orphan")
    participations = relationship("TournamentParticipant", back_populates="team")

    def __repr__(self) -> str:
        return f"<Team {self.name!r}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "name": self.name,
            "color": self.color,
            "member_count": len(self.members),
        }


# ---------------------------------------------------------------------------
# TeamPlayer (M2M: Team ↔ Player, unique per player per tournament)
# ---------------------------------------------------------------------------

class TeamPlayer(db.Model):
    __tablename__ = "team_players"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    team = relationship("Team", back_populates="members")
    player = relationship("Player", back_populates="team_memberships")

    # A player can only be in ONE team per tournament (enforced via trigger/app logic)
    __table_args__ = (
        UniqueConstraint("team_id", "player_id", name="uq_team_player"),
    )

    def to_dict(self) -> dict:
        return {
            "team_id": self.team_id,
            "player_id": self.player_id,
            "player_name": self.player.display_name if self.player else None,
        }


# ---------------------------------------------------------------------------
# TournamentParticipant
# ---------------------------------------------------------------------------

class TournamentParticipant(db.Model):
    __tablename__ = "tournament_participants"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    tournament_id = Column(
        Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False
    )
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # JSON-encoded metadata: seeding, notes, custom fields
    _meta = Column("meta", Text, nullable=True, default="{}")

    # Tracks if this participant was advanced to final stage (cutoff logic)
    advanced_to_final = Column(Boolean, default=False, nullable=False)
    is_eliminated = Column(Boolean, default=False, nullable=False)
    seed = Column(Integer, nullable=True)  # tournament seeding

    registered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tournament = relationship("Tournament", back_populates="participants")
    player = relationship("Player", back_populates="tournament_participations")
    team = relationship("Team", back_populates="participations")

    __table_args__ = (
        UniqueConstraint("tournament_id", "player_id", name="uq_tournament_participant"),
    )

    @property
    def meta(self) -> dict:
        try:
            return json.loads(self._meta or "{}")
        except Exception:
            return {}

    @meta.setter
    def meta(self, value: dict):
        self._meta = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "tournament_id": self.tournament_id,
            "player_id": self.player_id,
            "player_name": self.player.display_name if self.player else None,
            "team_id": self.team_id,
            "advanced_to_final": self.advanced_to_final,
            "is_eliminated": self.is_eliminated,
            "seed": self.seed,
            "meta": self.meta,
        }


# ---------------------------------------------------------------------------
# Game  (extended with tournament/stage FKs)
# ---------------------------------------------------------------------------

class Game(db.Model):
    __tablename__ = "games"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    played_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    win_side = Column(
        Enum(WinSide, name="win_side_enum"),
        nullable=False,
        default=WinSide.NONE,
    )
    notes = Column(Text, nullable=True)
    is_finished = Column(Boolean, default=False, nullable=False)

    # Tournament linkage (both nullable — standalone games have neither)
    tournament_id = Column(
        Integer, ForeignKey("tournaments.id", ondelete="SET NULL"), nullable=True
    )
    stage_id = Column(
        Integer, ForeignKey("tournament_stages.id", ondelete="SET NULL"), nullable=True
    )
    # Snapshot: is this game's result counted towards global rating?
    is_ranked = Column(Boolean, default=True, nullable=False)

    # Номер раунда внутри стадии турнира (NULL — не турнирная/ручная игра
    # без концепции раундов). Группирует игры, сыгранные "параллельно" за
    # разными столами одного раунда — см. TournamentService.generate_next_round.
    round_number = Column(Integer, nullable=True)

    # Season linkage (auto-assigned on game creation)
    season_id = Column(
        Integer, ForeignKey("seasons.id", ondelete="SET NULL"), nullable=True
    )

    slots = relationship(
        "GameSlot", back_populates="game", cascade="all, delete-orphan", lazy="joined"
    )
    tournament = relationship(
        "Tournament", back_populates="games", foreign_keys=[tournament_id]
    )
    stage = relationship(
        "TournamentStage", back_populates="games", foreign_keys=[stage_id]
    )
    season = relationship(
        "Season", back_populates="games", foreign_keys="[Game.season_id]"
    )

    __table_args__ = (
        CheckConstraint(
            "win_side IN ('mafia','city','none','MAFIA','CITY','NONE')",
            name="chk_win_side",
        ),
    )

    def __repr__(self) -> str:
        return f"<Game #{self.id} {self.played_at.date()}>"

    @property
    def player_count(self) -> int:
        return len(self.slots)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "played_at": self.played_at.isoformat(),
            "win_side": self.win_side.value,
            "is_finished": self.is_finished,
            "notes": self.notes,
            "tournament_id": self.tournament_id,
            "stage_id": self.stage_id,
            "is_ranked": self.is_ranked,
            "player_count": self.player_count,
        }


# ---------------------------------------------------------------------------
# GameSlot  (unchanged from original)
# ---------------------------------------------------------------------------

class GameSlot(db.Model):
    __tablename__ = "game_slots"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    seat_number = Column(Integer, nullable=False)
    role = Column(Enum(Role, name="role_enum"), nullable=False)

    base_score = Column(Float, default=0.0, nullable=False)
    bonus_score = Column(Float, default=0.0, nullable=False)
    is_eliminated = Column(Boolean, default=False, nullable=False)
    was_best_move = Column(Boolean, default=False, nullable=False)

    # ── PU (Первый Убиенный) ────────────────────────────────────────────────
    # is_pu: этот игрок был убит первым в ночь (без промаха).
    # Такой игрок называет 3 подозреваемых; pu_mafia_count — сколько
    # из них оказалось мафией (0, 1, 2 или 3).
    # PU-бонус к base_score: 0 мафий → 0.0, 1 → 0.1, 2 → 0.3, 3 → 0.6
    is_pu        = Column(Boolean, default=False, nullable=False)
    pu_mafia_count = Column(Integer, default=0, nullable=False)

    # ── ELO engine inputs (admin/judge assessed, optional) ──────────────────
    # quality_score (s_i): -1.0 .. +1.0, subjective performance rating
    quality_score = Column(Float, nullable=True)
    # pu_count: special standout actions count (b_i source for ELO)
    pu_count = Column(Integer, default=0, nullable=False)
    # elo_after: снимок ELO игрока сразу после применения этого матча —
    # только так можно построить график изменения ELO во времени (иначе
    # хранится только текущее Player.elo, без истории). Добавлено через
    # ALTER TABLE миграцию (migrate_elo_history.py) для существующих БД.
    elo_after = Column(Float, nullable=True)

    game = relationship("Game", back_populates="slots")
    player = relationship("Player", back_populates="game_slots")

    @validates("quality_score")
    def clamp_quality(self, key, value):
        if value is None:
            return None
        return max(-1.0, min(1.0, round(float(value), 3)))

    __table_args__ = (
        UniqueConstraint("game_id", "seat_number", name="uq_game_seat"),
        UniqueConstraint("game_id", "player_id", name="uq_game_player"),
        CheckConstraint("seat_number BETWEEN 1 AND 10", name="chk_seat_number"),
    )

    @validates("bonus_score")
    def round_bonus(self, key, value):
        return round(float(value), 2)

    @validates("base_score")
    def round_base(self, key, value):
        return round(float(value), 2)

    # PU bonus lookup table (immutable business rule)
    _PU_BONUS: dict[int, float] = {0: 0.0, 1: 0.1, 2: 0.3, 3: 0.6}

    @property
    def pu_bonus(self) -> float:
        """Bonus points from PU prediction. 0 if not PU."""
        if not self.is_pu:
            return 0.0
        count = max(0, min(3, self.pu_mafia_count or 0))
        return GameSlot._PU_BONUS.get(count, 0.0)

    @property
    def total_score(self) -> float:
        return round(self.base_score + self.bonus_score + self.pu_bonus, 2)

    @property
    def is_mafia_side(self) -> bool:
        return self.role in (Role.MAFIA, Role.DON)

    @property
    def is_city_side(self) -> bool:
        return self.role in (Role.CIVILIAN, Role.SHERIFF)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "game_id": self.game_id,
            "player_id": self.player_id,
            "player_name": self.player.display_name if self.player else None,
            "seat_number": self.seat_number,
            "role": self.role.value,
            "base_score": self.base_score,
            "bonus_score": self.bonus_score,
            "pu_bonus": self.pu_bonus,
            "total_score": self.total_score,
            "is_eliminated": self.is_eliminated,
            "is_pu": self.is_pu,
            "pu_mafia_count": self.pu_mafia_count,
            "quality_score": self.quality_score,
            "elo_after": self.elo_after,
        }

# ---------------------------------------------------------------------------
# User  (auth — imported last to avoid circular refs)
# ---------------------------------------------------------------------------
from app.models.user import User  # noqa: E402,F401


# ---------------------------------------------------------------------------
# Season  (автоматические двухмесячные сезоны)
# ---------------------------------------------------------------------------

class SeasonStatus(PyEnum):
    ACTIVE         = "active"          # идёт прямо сейчас
    FINISHED       = "finished"        # завершён, победитель определён
    WAITING_TIEBREAK = "waiting_tiebreak"  # ничья — нужен ручной выбор


class Season(db.Model):
    __tablename__ = "seasons"
    __allow_unmapped__ = True

    id         = Column(Integer, primary_key=True)
    year       = Column(Integer, nullable=False)
    number     = Column(Integer, nullable=False)   # 1-6 внутри года
    name       = Column(String(40), nullable=False) # "Сезон 1 (Янв–Фев) 2025"

    # Фиксированные границы периода (UTC-полночь)
    starts_at  = Column(DateTime(timezone=True), nullable=False)
    ends_at    = Column(DateTime(timezone=True), nullable=False)

    status     = Column(
        Enum(SeasonStatus, name="season_status_enum"),
        nullable=False,
        default=SeasonStatus.ACTIVE,
    )

    # Победитель (заполняется при завершении)
    winner_player_id = Column(
        Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True
    )
    winner_score     = Column(Float, nullable=True)

    # Ссылка на «Стол года»: участие победителя добавляется автоматически
    year_tournament_id = Column(
        Integer, ForeignKey("tournaments.id", ondelete="SET NULL"), nullable=True
    )

    winner  = relationship("Player", foreign_keys=[winner_player_id])
    games   = relationship("Game",   back_populates="season", foreign_keys="Game.season_id")

    __table_args__ = (
        UniqueConstraint("year", "number", name="uq_season_year_number"),
    )

    def __repr__(self) -> str:
        return f"<Season {self.name} [{self.status.value}]>"

    @property
    def is_over(self) -> bool:
        """True если период сезона уже завершился по времени."""
        ends = self.ends_at
        if ends.tzinfo is None:
            ends = ends.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > ends

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "year":        self.year,
            "number":      self.number,
            "name":        self.name,
            "starts_at":   self.starts_at.isoformat(),
            "ends_at":     self.ends_at.isoformat(),
            "status":      self.status.value,
            "is_over":     self.is_over,
            "winner_player_id": self.winner_player_id,
            "winner_score":     self.winner_score,
            "winner_name":  self.winner.display_name if self.winner else None,
        }


# ===========================================================================
# Extended Player fields (added in v5)
# ===========================================================================
# These are added via ALTER TABLE migration for existing DBs.
# Declared here so SQLAlchemy sees them on create_all().
# avatar_url, bio, coins already patched in via migration helper.


# ===========================================================================
# CoinTransaction  — economy ledger
# ===========================================================================

class CoinSourceType(PyEnum):
    GAME_REWARD        = "game_reward"
    TOURNAMENT_REWARD  = "tournament_reward"
    SEASON_REWARD      = "season_reward"
    SYSTEM_BONUS       = "system_bonus"
    ADMIN_ADJUSTMENT   = "admin_adjustment"
    FANTASY_REWARD     = "fantasy_reward"
    PURCHASE           = "purchase"    # future
    RESALE_PAYOUT      = "resale_payout"  # ShopService.buyout_item() — выплата прежнему владельцу


class CoinTransaction(db.Model):
    __tablename__ = "coin_transactions"
    __allow_unmapped__ = True

    id          = Column(Integer, primary_key=True)
    player_id   = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    amount      = Column(Float, nullable=False)          # positive = credit, negative = debit
    balance_after = Column(Float, nullable=False)        # snapshot for audit trail
    reason      = Column(String(255), nullable=False)
    source_type = Column(
        Enum(CoinSourceType, name="coin_source_type_enum"), nullable=False
    )
    ref_game_id       = Column(Integer, ForeignKey("games.id", ondelete="SET NULL"), nullable=True)
    ref_tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="SET NULL"), nullable=True)
    created_at  = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    player = relationship("Player", foreign_keys=[player_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "player_id": self.player_id,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "reason": self.reason,
            "source_type": self.source_type.value,
            "created_at": self.created_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# EconomySettings — single-row table of admin-editable economy parameters.
# Anything that should stay a hardcoded constant remains in economy_service.py;
# this table is only for parameters an admin can change at runtime from
# /admin/economy (currently: Fantasy entry cost & prize split).
# ---------------------------------------------------------------------------

class EconomySettings(db.Model):
    __tablename__ = "economy_settings"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)

    fantasy_entry_cost         = Column(Float, nullable=False, default=100.0)
    fantasy_first_place_share  = Column(Float, nullable=False, default=0.70)
    fantasy_second_place_share = Column(Float, nullable=False, default=0.30)

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "fantasy_entry_cost": self.fantasy_entry_cost,
            "fantasy_first_place_share": self.fantasy_first_place_share,
            "fantasy_second_place_share": self.fantasy_second_place_share,
            "updated_at": self.updated_at.isoformat(),
        }


# ===========================================================================
# Fantasy Draft
# ===========================================================================

class FantasyDraftStatus(PyEnum):
    OPEN     = "open"       # picks can be changed
    LOCKED   = "locked"     # tournament started, picks frozen
    SCORED   = "scored"     # tournament finished, points calculated


class FantasyDraft(db.Model):
    __tablename__ = "fantasy_drafts"
    __allow_unmapped__ = True

    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    total_points  = Column(Float, default=0.0, nullable=False)
    # Entry fee actually charged at draft creation time (snapshot of
    # EconomySettings.fantasy_entry_cost at that moment). Used to compute
    # the prize pool so a later admin change to the entry cost can't alter
    # the payout of a tournament that already started.
    # Added via ALTER TABLE migration for existing DBs — see migrate_fantasy_economy.py.
    entry_cost_paid = Column(Float, default=0.0, nullable=False, server_default="0")
    status        = Column(
        Enum(FantasyDraftStatus, name="fantasy_draft_status_enum"),
        nullable=False,
        default=FantasyDraftStatus.OPEN,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    scored_at  = Column(DateTime(timezone=True), nullable=True)

    user       = relationship("User",       foreign_keys=[user_id])
    tournament = relationship("Tournament", foreign_keys=[tournament_id])
    picks      = relationship(
        "FantasyDraftPick",
        back_populates="draft",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "tournament_id", name="uq_fantasy_user_tournament"),
    )

    @property
    def pick_count(self) -> int:
        return len(self.picks)

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "user_id":       self.user_id,
            "tournament_id": self.tournament_id,
            "total_points":  self.total_points,
            "entry_cost_paid": self.entry_cost_paid,
            "status":        self.status.value,
            "pick_count":    self.pick_count,
            "created_at":    self.created_at.isoformat(),
            "picks": [p.to_dict() for p in self.picks],
        }


class FantasyDraftPick(db.Model):
    __tablename__ = "fantasy_draft_picks"
    __allow_unmapped__ = True

    id           = Column(Integer, primary_key=True)
    draft_id     = Column(Integer, ForeignKey("fantasy_drafts.id", ondelete="CASCADE"), nullable=False)
    player_id    = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"),  nullable=False)
    points_earned = Column(Float, default=0.0, nullable=False)

    draft  = relationship("FantasyDraft", back_populates="picks")
    player = relationship("Player", foreign_keys=[player_id])

    __table_args__ = (
        UniqueConstraint("draft_id", "player_id", name="uq_fantasy_pick_player"),
    )

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "draft_id":     self.draft_id,
            "player_id":    self.player_id,
            "player_name":  self.player.display_name if self.player else None,
            "points_earned": self.points_earned,
        }


# ---------------------------------------------------------------------------
# GG  (admin-granted seasonal bonus — "Good Game" points)
# ---------------------------------------------------------------------------

class GG(db.Model):
    """
    Admin-assigned bonus tied to exactly one season.
    Influences ONLY SeasonRating, never ELO or global rating.
    Immutable ledger entry — never UPDATE, only INSERT (+ optional soft revoke).
    """
    __tablename__ = "gg_bonuses"
    __allow_unmapped__ = True

    id         = Column(Integer, primary_key=True)
    player_id  = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    season_id  = Column(Integer, ForeignKey("seasons.id",  ondelete="CASCADE"), nullable=False)
    value      = Column(Float, nullable=False)               # can be negative (penalty)
    reason     = Column(String(255), nullable=False)
    admin_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    revoked    = Column(Boolean, default=False, nullable=False)

    player  = relationship("Player", foreign_keys=[player_id])
    season  = relationship("Season", foreign_keys=[season_id])
    admin   = relationship("User",   foreign_keys=[admin_id])

    @validates("value")
    def round_value(self, key, value):
        return round(float(value), 2)

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "player_id":  self.player_id,
            "season_id":  self.season_id,
            "value":      self.value,
            "reason":     self.reason,
            "admin_id":   self.admin_id,
            "admin_name": self.admin.username if self.admin else None,
            "created_at": self.created_at.isoformat(),
            "revoked":    self.revoked,
        }


# ===========================================================================
# Shop / Inventory / Achievements  (v6 — customization, cosmetics, goals)
# ===========================================================================

class ShopCategory(PyEnum):
    PROFILE_CUSTOMIZATION = "profile_customization"
    NICKNAME              = "nickname"
    PHYSICAL              = "physical"


class Rarity(PyEnum):
    COMMON    = "common"
    RARE      = "rare"
    EPIC      = "epic"
    LEGENDARY = "legendary"
    MYTHIC    = "mythic"    # уникальные предметы — см. ShopService.buyout_item()
    ULTRA     = "ultra"     # уникальные предметы — см. ShopService.buyout_item()


class AchievementCategory(PyEnum):
    GAMES       = "games"
    WINS        = "wins"
    RATING      = "rating"
    TOURNAMENTS = "tournaments"
    SEASONS     = "seasons"
    FANTASY     = "fantasy"
    ECONOMY     = "economy"
    SOCIAL      = "social"
    SPECIAL     = "special"


class AchievementTrigger(PyEnum):
    GAME       = "game"
    TOURNAMENT = "tournament"
    SEASON     = "season"
    PURCHASE   = "purchase"  # checked right after a shop purchase
    MANUAL     = "manual"    # admin-granted or event-driven one-shot unlock, no rule check


# ---------------------------------------------------------------------------
# ShopItem
# ---------------------------------------------------------------------------

class ShopItem(db.Model):
    """
    Purchasable item. `category` + `subcategory` together define the equip
    "slot" — equipping a new item in a slot auto-unequips any other item
    already equipped in that same slot for that player (see ShopService).
    New subcategories need zero code changes; the slot logic is data-driven.

    `data` is a free-form JSON payload for the cosmetic effect (hex color,
    gradient stops, animation name, prefix/suffix text, frame/background CSS
    class, stat-theme name, …) — same pattern as TournamentParticipant.meta.
    """
    __tablename__ = "shop_items"
    __allow_unmapped__ = True

    id          = Column(Integer, primary_key=True)
    name        = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    category    = Column(Enum(ShopCategory, name="shop_category_enum"), nullable=False)
    subcategory = Column(String(40), nullable=False)
    rarity      = Column(Enum(Rarity, name="rarity_enum"), nullable=False, default=Rarity.COMMON)
    price       = Column(Float, nullable=False)
    image_url   = Column(String(512), nullable=True)
    is_active   = Column(Boolean, default=True, nullable=False)

    # Whether a player may own at most ONE InventoryItem for this ShopItem.
    # True for cosmetics (buying "Golden Frame" twice is pointless); False
    # for PHYSICAL items where repeat purchase is expected (e.g. a T-shirt).
    is_unique_purchase = Column(Boolean, default=True, nullable=False)

    # ── Gifting (added via ALTER TABLE migration — migrate_gifting.py) ──────
    # Может ли этот предмет быть подарен другому игроку.
    is_transferable  = Column(Boolean, default=True, nullable=False, server_default="1")
    # Разрешено ли прикладывать личное сообщение к подарку этим предметом.
    giftable_message = Column(Boolean, default=True, nullable=False, server_default="1")

    _data = Column("data", Text, nullable=True, default="{}")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    inventory_entries = relationship(
        "InventoryItem", back_populates="item", cascade="all, delete-orphan"
    )

    @property
    def data(self) -> dict:
        try:
            return json.loads(self._data or "{}")
        except Exception:
            return {}

    @data.setter
    def data(self, value: dict):
        self._data = json.dumps(value or {})

    @property
    def slot_key(self) -> str:
        """Identifies the equip slot this item competes for."""
        return f"{self.category.value}:{self.subcategory}"

    def __repr__(self) -> str:
        return f"<ShopItem {self.name!r} [{self.category.value}/{self.subcategory}]>"

    def to_dict(self) -> dict:
        return {
            "id":                 self.id,
            "name":               self.name,
            "description":        self.description,
            "category":           self.category.value,
            "subcategory":        self.subcategory,
            "rarity":             self.rarity.value,
            "price":              self.price,
            "image_url":          self.image_url,
            "is_active":          self.is_active,
            "is_unique_purchase": self.is_unique_purchase,
            "is_transferable":    self.is_transferable,
            "giftable_message":   self.giftable_message,
            "data":               self.data,
            "created_at":         self.created_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# InventoryItem  (ownership + equip state)
# ---------------------------------------------------------------------------

class InventoryItem(db.Model):
    """
    A player's owned copy of a ShopItem. Purchase-uniqueness (when
    item.is_unique_purchase) is enforced in ShopService, not by a DB
    constraint — same trust level as TeamPlayer's app-enforced uniqueness.
    """
    __tablename__ = "inventory_items"
    __allow_unmapped__ = True

    id        = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    item_id   = Column(Integer, ForeignKey("shop_items.id", ondelete="CASCADE"), nullable=False)

    acquired_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    price_paid  = Column(Float, nullable=False, default=0.0)  # snapshot at purchase time
    is_equipped = Column(Boolean, default=False, nullable=False)
    source      = Column(String(30), nullable=False, default="purchase")  # purchase | admin_grant

    player = relationship("Player", foreign_keys=[player_id])
    item   = relationship("ShopItem", back_populates="inventory_entries")

    __table_args__ = (
        Index("ix_inventory_player_item", "player_id", "item_id"),
    )

    def __repr__(self) -> str:
        return f"<InventoryItem player={self.player_id} item={self.item_id} equipped={self.is_equipped}>"

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "player_id":   self.player_id,
            "item_id":     self.item_id,
            "item":        self.item.to_dict() if self.item else None,
            "acquired_at": self.acquired_at.isoformat(),
            "price_paid":  self.price_paid,
            "is_equipped": self.is_equipped,
            "source":      self.source,
        }


# ---------------------------------------------------------------------------
# Achievement  (admin-editable presentation, linked to a rule via `code`)
# ---------------------------------------------------------------------------

class Achievement(db.Model):
    """
    Presentation row for an achievement. `code` links this row to a checker
    function in app/services/achievement_rules.py — adding a new achievement
    means adding one rule-registry entry + one seeded row with matching code,
    never touching the AchievementService dispatch loop (Open/Closed).
    """
    __tablename__ = "achievements"
    __allow_unmapped__ = True

    id          = Column(Integer, primary_key=True)
    code        = Column(String(64), nullable=False, unique=True)
    name        = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    icon        = Column(String(64), nullable=True)  # bootstrap-icon class, e.g. "bi-trophy-fill"
    category    = Column(Enum(AchievementCategory, name="achievement_category_enum"), nullable=False)
    rarity      = Column(Enum(Rarity, name="rarity_enum"), nullable=False, default=Rarity.COMMON)
    trigger     = Column(Enum(AchievementTrigger, name="achievement_trigger_enum"), nullable=False)
    is_hidden   = Column(Boolean, default=False, nullable=False)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    unlocks = relationship(
        "PlayerAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Achievement {self.code!r} [{self.category.value}]>"

    def to_dict(self, unlocked: bool = True) -> dict:
        """When unlocked=False and is_hidden, redact spoilers."""
        if self.is_hidden and not unlocked:
            return {
                "id":          self.id,
                "code":        self.code,
                "name":        "???",
                "description": "Скрытое достижение",
                "icon":        "bi-question-circle",
                "category":    self.category.value,
                "rarity":      self.rarity.value,
                "is_hidden":   True,
                "unlocked":    False,
            }
        return {
            "id":          self.id,
            "code":        self.code,
            "name":        self.name,
            "description": self.description,
            "icon":        self.icon,
            "category":    self.category.value,
            "rarity":      self.rarity.value,
            "is_hidden":   self.is_hidden,
            "unlocked":    unlocked,
        }


# ---------------------------------------------------------------------------
# PlayerAchievement  (unlock ledger)
# ---------------------------------------------------------------------------

class PlayerAchievement(db.Model):
    __tablename__ = "player_achievements"
    __allow_unmapped__ = True

    id             = Column(Integer, primary_key=True)
    player_id      = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at    = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    pinned       = Column(Boolean, default=False, nullable=False)
    pinned_order = Column(Integer, nullable=True)  # 1..3 when pinned

    player      = relationship("Player", foreign_keys=[player_id])
    achievement = relationship("Achievement", back_populates="unlocks")

    __table_args__ = (
        UniqueConstraint("player_id", "achievement_id", name="uq_player_achievement"),
    )

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "player_id":      self.player_id,
            "achievement_id": self.achievement_id,
            "achievement":    self.achievement.to_dict(unlocked=True) if self.achievement else None,
            "unlocked_at":    self.unlocked_at.isoformat(),
            "pinned":         self.pinned,
            "pinned_order":   self.pinned_order,
        }


# ===========================================================================
# Titles / Nominations  (v7 — seasonal role awards + club-wide record titles)
# ===========================================================================

class TitleType(PyEnum):
    SEASONAL = "seasonal"  # awarded once per season, permanent historical record
    ETERNAL  = "eternal"   # "current record holder" — may be reassigned on recompute
    MANUAL   = "manual"    # admin-granted, no automatic rule


# ---------------------------------------------------------------------------
# Title  (presentation/definition row, matched by `code` from NominationService)
# ---------------------------------------------------------------------------

class Title(db.Model):
    """
    Definition of a title a player can hold. `code` links this row to the
    scoring logic in app/services/nomination_service.py — same registry-key
    idea as Achievement.code. Not a per-player fact; see PlayerTitle for that.
    """
    __tablename__ = "titles"
    __allow_unmapped__ = True

    id          = Column(Integer, primary_key=True)
    code        = Column(String(64), nullable=False, unique=True)
    name        = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    icon        = Column(String(64), nullable=True)  # bootstrap-icon class
    rarity      = Column(Enum(Rarity, name="rarity_enum"), nullable=False, default=Rarity.COMMON)
    type        = Column(Enum(TitleType, name="title_type_enum"), nullable=False)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    awards = relationship(
        "PlayerTitle", back_populates="title", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Title {self.code!r} [{self.type.value}]>"

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "code":        self.code,
            "name":        self.name,
            "description": self.description,
            "icon":        self.icon,
            "rarity":      self.rarity.value,
            "type":        self.type.value,
            "is_active":   self.is_active,
        }


# ---------------------------------------------------------------------------
# PlayerTitle  (award ledger + equip state)
# ---------------------------------------------------------------------------

class PlayerTitle(db.Model):
    """
    One award of a Title to a Player.

    SEASONAL awards are permanent historical facts (season_id records which
    season it was won, never revoked by recomputation — this is what makes
    "история прошлых сезонных победителей" meaningful).

    ETERNAL awards describe the *current* club-wide record holder, like a
    "reigning champion" belt: recomputing (TitleService.revoke_current_holder_if_any
    + grant_title) revokes the old holder's row and grants a fresh one to
    whoever now holds the record — the only reading of "вечный" that stays
    correct as more games are played.

    Dedup (one award per player+title+season) is a service-level pre-check,
    same trust level as InventoryItem's purchase-uniqueness.
    """
    __tablename__ = "player_titles"
    __allow_unmapped__ = True

    id        = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    title_id  = Column(Integer, ForeignKey("titles.id", ondelete="CASCADE"), nullable=False)

    # Set only for SEASONAL awards — permanently records which season was won.
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="SET NULL"), nullable=True)

    equipped = Column(Boolean, default=False, nullable=False)
    revoked  = Column(Boolean, default=False, nullable=False)  # soft-delete, same precedent as GG.revoked

    granted_by = Column(String(20), nullable=False, default="system")  # system | admin
    admin_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason     = Column(Text, nullable=True)  # required when granted_by="admin"

    awarded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    player = relationship("Player", foreign_keys=[player_id])
    title  = relationship("Title", back_populates="awards")
    season = relationship("Season", foreign_keys=[season_id])
    admin  = relationship("User", foreign_keys=[admin_id])

    __table_args__ = (
        Index("ix_player_title_player", "player_id"),
        Index("ix_player_title_title", "title_id"),
    )

    def __repr__(self) -> str:
        return f"<PlayerTitle player={self.player_id} title={self.title_id} equipped={self.equipped}>"

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "player_id":  self.player_id,
            "player_name": self.player.display_name if self.player else None,
            "title_id":   self.title_id,
            "title":      self.title.to_dict() if self.title else None,
            "season_id":  self.season_id,
            "season_name": self.season.name if self.season else None,
            "equipped":   self.equipped,
            "revoked":    self.revoked,
            "granted_by": self.granted_by,
            "reason":     self.reason,
            "awarded_at": self.awarded_at.isoformat(),
        }


# ===========================================================================
# GiftTransfer  (v8 — маркетплейс подарков между игроками)
# ===========================================================================

class GiftTransfer(db.Model):
    """
    Лог передачи InventoryItem от одного игрока другому. Передача мгновенная
    (не pending/accept-flow) — владение InventoryItem.player_id меняется сразу
    в GiftService.send_gift(), эта запись только исторический след + источник
    для бейджа "непрочитанных подарков" (seen=False, чисто pull-based, без
    websocket — читается при обычной загрузке страницы, как и #nav-coins).
    """
    __tablename__ = "gift_transfers"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False)
    # Снимок товара на момент передачи — история отображается без лишнего
    # JOIN, даже если сам InventoryItem потом снова сменит владельца.
    shop_item_id = Column(Integer, ForeignKey("shop_items.id", ondelete="SET NULL"), nullable=True)

    from_player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    to_player_id   = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)

    message = Column(Text, nullable=True)
    seen    = Column(Boolean, default=False, nullable=False)

    transferred_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    inventory_item = relationship("InventoryItem", foreign_keys=[inventory_item_id])
    shop_item      = relationship("ShopItem", foreign_keys=[shop_item_id])
    from_player    = relationship("Player", foreign_keys=[from_player_id])
    to_player      = relationship("Player", foreign_keys=[to_player_id])

    def __repr__(self) -> str:
        return f"<GiftTransfer {self.from_player_id}->{self.to_player_id} item={self.shop_item_id}>"

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "inventory_item_id": self.inventory_item_id,
            "shop_item":        self.shop_item.to_dict() if self.shop_item else None,
            "from_player_id":   self.from_player_id,
            "from_player_name": self.from_player.display_name if self.from_player else None,
            "to_player_id":     self.to_player_id,
            "to_player_name":   self.to_player.display_name if self.to_player else None,
            "message":          self.message,
            "seen":             self.seen,
            "transferred_at":   self.transferred_at.isoformat(),
        }


# ===========================================================================
# Серийные турниры  (v9 — один большой турнир из нескольких игровых вечеров)
# ===========================================================================
#
# Намеренно тонкие обёртки поверх уже существующих Tournament/TournamentStage:
# SeriesTournament не хранит name/status/description — они уже есть на
# Tournament (доступны через .tournament.*). Серия ("игровой вечер") — это
# TournamentStage с независимой (не эксклюзивной) активацией; вся игровая
# механика (Game.stage_id, RatingService.get_stage_rating/get_tournament_rating)
# переиспользуется как есть, без единой новой строчки в логике подсчёта очков.

class SeriesStatus(PyEnum):
    PENDING   = "pending"
    ACTIVE    = "active"
    FINISHED  = "finished"
    CANCELLED = "cancelled"


class SeriesTournament(db.Model):
    """
    1:1 обёртка над Tournament, помечающая его как «серийный турнир» —
    для отдельного списка/страниц и более богатого сквозного лидерборда
    по сериям. Название/статус/описание не дублируются — берутся из
    self.tournament.
    """
    __tablename__ = "series_tournaments"
    __allow_unmapped__ = True

    id            = Column(Integer, primary_key=True)
    tournament_id = Column(
        Integer, ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tournament = relationship("Tournament", foreign_keys=[tournament_id])
    series = relationship(
        "TournamentSeries", back_populates="series_tournament",
        cascade="all, delete-orphan", order_by="TournamentSeries.order",
    )

    def __repr__(self) -> str:
        return f"<SeriesTournament tournament_id={self.tournament_id}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "tournament": self.tournament.to_dict() if self.tournament else None,
            "series_count": len(self.series),
            "created_at": self.created_at.isoformat(),
        }


class TournamentSeries(db.Model):
    """
    Одна серия («игровой вечер») внутри серийного турнира. stage_id —
    реальная связь на существующий TournamentStage: именно через него
    игры (Game.stage_id) и рейтинг (RatingService.get_stage_rating)
    переиспользуются без изменений. status — свой (не путать со
    status у TournamentStage) специально ради CANCELLED, которого у
    обычных этапов турнирной сетки нет.
    """
    __tablename__ = "tournament_series"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    series_tournament_id = Column(
        Integer, ForeignKey("series_tournaments.id", ondelete="CASCADE"), nullable=False
    )
    stage_id = Column(
        Integer, ForeignKey("tournament_stages.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    name = Column(String(120), nullable=False)
    series_date = Column(Date, nullable=True)
    order = Column(Integer, nullable=False, default=0)
    status = Column(
        Enum(SeriesStatus, name="series_status_enum"),
        nullable=False, default=SeriesStatus.PENDING,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    series_tournament = relationship("SeriesTournament", back_populates="series")
    stage = relationship("TournamentStage", foreign_keys=[stage_id])

    __table_args__ = (
        UniqueConstraint("series_tournament_id", "order", name="uq_series_order"),
    )

    def __repr__(self) -> str:
        return f"<TournamentSeries {self.name!r} [{self.status.value}]>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "series_tournament_id": self.series_tournament_id,
            "stage_id": self.stage_id,
            "name": self.name,
            "series_date": self.series_date.isoformat() if self.series_date else None,
            "order": self.order,
            "status": self.status.value,
            "games_count": len(self.stage.games) if self.stage else 0,
            "created_at": self.created_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# LegacyImportMap  (Migration API — импорт из старой версии приложения)
# ---------------------------------------------------------------------------
from app.models.migration import LegacyImportMap  # noqa: E402,F401
