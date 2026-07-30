"""
ExternalGameImportService
=========================
Приём завершённых игр от внешних сервисов (сейчас: MafiaSpace) через
вебхук и превращение их в настоящие Game/GameSlot, посчитанные тем же
движком, что и игры, заведённые вручную (PostGameOrchestrator).

Design rules:
  - Никогда не доверяем чужим предпосчитанным очкам/фолам — base_score
    считается нашим RatingService из роли+результата+ПУ, как для любой
    другой игры на сайте. Это единственный способ не рассинхронизировать
    компенсацию/ELO/рейтинг между локальными и импортированными играми.
  - Игрок сопоставляется только через явную ExternalPlayerLink — никогда
    не угадывается по нику молча. Несопоставленные игроки уходят в
    очередь на подтверждение админом (ExternalGameImport.status=
    "pending_review"), настоящая Game не создаётся, пока все не решены.
  - external_id — ключ идемпотентности: повторный вебхук с тем же
    external_id не создаёт вторую игру и не трогает уже импортированную
    (см. docstring на find_or_create_import).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app import db
from app.models import (
    Game, GameSlot, Player, Role, WinSide,
    ExternalPlayerLink, ExternalGameImport,
)
from app.services.economy_service import EconomyService
from app.services.orchestrator import PostGameOrchestrator

SOURCE = "mafiaspace"

_WINNER_MAP = {"city": WinSide.CITY, "mafia": WinSide.MAFIA, "draw": WinSide.NONE}


@dataclass
class ImportOutcome:
    ok: bool
    message: str
    import_row: Optional[ExternalGameImport] = None
    game: Optional[Game] = None
    unmatched: List[dict] = field(default_factory=list)


def _parse_played_at(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


class ExternalGameImportService:

    # ── Idempotency ──────────────────────────────────────────────────────────

    @staticmethod
    def get_existing_import(external_id: str) -> Optional[ExternalGameImport]:
        return (
            db.session.query(ExternalGameImport)
            .filter_by(source=SOURCE, external_id=external_id)
            .first()
        )

    # ── Player matching ──────────────────────────────────────────────────────

    @staticmethod
    def match_players(players_payload: List[dict]) -> tuple[Dict[int, Player], List[dict]]:
        """
        Returns (matched: {seat: Player}, unmatched: [player_payload, ...]).
        Only ever matches via an existing ExternalPlayerLink — never guesses
        by nickname text, since two different real people can share a nick.
        """
        matched: Dict[int, Player] = {}
        unmatched: List[dict] = []
        for p in players_payload:
            link = (
                db.session.query(ExternalPlayerLink)
                .filter_by(source=SOURCE, external_id=p["external_id"])
                .first()
            )
            if link:
                matched[p["seat"]] = link.player
            else:
                unmatched.append(p)
        return matched, unmatched

    # ── Core game construction (shared by webhook + admin resolver) ─────────

    @staticmethod
    def _compute_pu(slots_by_seat: Dict[int, GameSlot], payload: dict) -> None:
        """
        Их killed_first/best_move несёт КОГО назвали, не сколько из них
        реально мафия — это мы сами считаем, сверяя called_seats с ролями,
        которые только что проставили на слоты (роли есть в этом же payload).
        """
        killed_first = payload.get("killed_first")
        if not killed_first:
            return
        seat = killed_first.get("seat")
        slot = slots_by_seat.get(seat)
        if not slot:
            return
        slot.is_pu = True

        best_move = payload.get("best_move") or {}
        called_seats = best_move.get("called_seats") or []
        correct = sum(
            1 for s in called_seats
            if slots_by_seat.get(s) and slots_by_seat[s].role in (Role.MAFIA, Role.DON)
        )
        slot.pu_mafia_count = max(0, min(3, correct))

    @staticmethod
    def build_and_finish_game(payload: dict, player_by_seat: Dict[int, Player]) -> tuple[Optional[Game], Optional[str]]:
        """
        Builds a real, fully-scored Game from a MafiaSpace payload plus an
        already-resolved seat->Player map. Mirrors games.py's finish_game()
        slot population + role-distribution validation, then hands off to
        PostGameOrchestrator.run() — the same pipeline manual games use.
        Returns (game, None) on success or (None, error_message) on failure.
        """
        players_payload = payload["players"]

        seen_player_ids: Dict[int, int] = {}  # player_id -> first seat seen at
        for p in players_payload:
            seat = p["seat"]
            player = player_by_seat[seat]
            if player.id in seen_player_ids:
                return None, (
                    f"Игрок «{player.display_name}» указан сразу на местах "
                    f"{seen_player_ids[player.id]} и {seat} — выберите разных игроков."
                )
            seen_player_ids[player.id] = seat

        game = Game(
            is_finished=False,
            win_side=WinSide.NONE,
            played_at=_parse_played_at(payload.get("played_at")),
            is_ranked=True,
            tournament_id=None,
            stage_id=None,
        )
        db.session.add(game)
        db.session.flush()

        slots_by_seat: Dict[int, GameSlot] = {}
        for p in players_payload:
            seat = p["seat"]
            player = player_by_seat[seat]
            try:
                role = Role(p["role"])
            except ValueError:
                db.session.rollback()
                return None, f"Неизвестная роль «{p.get('role')}» на месте {seat}."
            slot = GameSlot(game_id=game.id, player_id=player.id, seat_number=seat, role=role)
            db.session.add(slot)
            slots_by_seat[seat] = slot
        db.session.flush()

        role_values = [s.role.value for s in slots_by_seat.values()]
        if all(v == "civilian" for v in role_values):
            db.session.rollback()
            return None, "Все роли — мирный, протокол выглядит некорректным."
        if role_values.count("mafia") + role_values.count("don") == 0:
            db.session.rollback()
            return None, "В протоколе нет ни одной роли мафии/дона."

        ExternalGameImportService._compute_pu(slots_by_seat, payload)

        winner = (payload.get("winner") or "none").lower()
        game.win_side = _WINNER_MAP.get(winner, WinSide.NONE)

        game.is_finished = True
        db.session.flush()

        PostGameOrchestrator.run(game)
        return game, None

    # ── Webhook entry point ──────────────────────────────────────────────────

    @staticmethod
    def ingest_webhook_payload(payload: dict) -> ImportOutcome:
        external_id = payload.get("external_id")
        if not external_id:
            return ImportOutcome(ok=False, message="external_id обязателен.")

        existing = ExternalGameImportService.get_existing_import(external_id)
        if existing:
            # Идемпотентность: тот же external_id повторно не пересоздаёт и
            # не обновляет игру (см. docstring модуля) — просто отдаём тот
            # же результат, что и в первый раз.
            return ImportOutcome(ok=True, message="Уже обработано ранее.", import_row=existing, game=existing.game)

        players_payload = payload.get("players") or []
        matched, unmatched = ExternalGameImportService.match_players(players_payload)

        if unmatched:
            import_row = ExternalGameImport(
                source=SOURCE,
                external_id=external_id,
                raw_payload=json.dumps(payload, ensure_ascii=False),
                status="pending_review",
            )
            db.session.add(import_row)
            db.session.commit()
            return ImportOutcome(
                ok=True, message="Часть игроков не сопоставлена, отправлено на ручное подтверждение.",
                import_row=import_row, unmatched=unmatched,
            )

        game, error = ExternalGameImportService.build_and_finish_game(payload, matched)
        if error:
            return ImportOutcome(ok=False, message=error)

        import_row = ExternalGameImport(
            source=SOURCE,
            external_id=external_id,
            raw_payload=json.dumps(payload, ensure_ascii=False),
            status="imported",
            game_id=game.id,
            resolved_at=datetime.now(timezone.utc),
        )
        db.session.add(import_row)
        db.session.commit()
        return ImportOutcome(ok=True, message="Игра импортирована.", import_row=import_row, game=game)

    # ── Admin resolution of a pending import ─────────────────────────────────

    @staticmethod
    def resolve_pending_import(import_row: ExternalGameImport, resolutions: Dict[int, dict]) -> tuple[Optional[Game], Optional[str]]:
        """
        resolutions: {seat: {"player_id": int}} or {seat: {"create_new": True}}
        for every seat that was originally unmatched. Creates an
        ExternalPlayerLink for each so future games from the same external_id
        auto-match without another trip through this queue.
        """
        payload = json.loads(import_row.raw_payload)
        players_payload = payload.get("players") or []
        matched, unmatched = ExternalGameImportService.match_players(players_payload)

        for p in unmatched:
            seat = p["seat"]
            choice = resolutions.get(seat) or {}
            if choice.get("create_new"):
                nickname = p["nickname"]
                player = Player(nickname=nickname, name=nickname)
                db.session.add(player)
                db.session.flush()
                EconomyService.grant_welcome_bonus(player)
            else:
                player_id = choice.get("player_id")
                player = db.session.get(Player, player_id) if player_id else None
                if not player:
                    return None, f"Не выбран игрок для места {seat} («{p['nickname']}»)."

            db.session.add(ExternalPlayerLink(
                source=SOURCE, external_id=p["external_id"],
                nickname_hint=p["nickname"], player_id=player.id,
            ))
            matched[seat] = player

        db.session.flush()

        game, error = ExternalGameImportService.build_and_finish_game(payload, matched)
        if error:
            db.session.rollback()
            return None, error

        import_row.status = "imported"
        import_row.game_id = game.id
        import_row.resolved_at = datetime.now(timezone.utc)
        db.session.commit()
        return game, None
