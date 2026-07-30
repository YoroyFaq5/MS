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
  - Игрок сопоставляется через ExternalPlayerLink, а если её ещё нет —
    автоматически по нику, но ТОЛЬКО когда это однозначно: используем
    PlayerSearchService.normalize_for_match() (тот же транслит+регистр
    normalize, что уже защищает от дублей "Virus"/"Вирус" при создании
    игрока) и авто-привязываем, если находится РОВНО один такой игрок
    клуба — и сразу создаём ExternalPlayerLink, чтобы больше не искать
    по нику вообще. Ноль или больше одного совпадения — не угадываем,
    уходит в очередь на подтверждение админом (ExternalGameImport.status=
    "pending_review"), настоящая Game не создаётся, пока все не решены.
  - external_id — ключ идемпотентности: повторный вебхук с тем же
    external_id никогда не создаёт вторую игру. Если игра уже была
    импортирована — считаем это исправленным протоколом и обновляем её
    на месте через EditGameOrchestrator (см. update_existing_game). Если
    ещё висит в очереди на подтверждение — просто освежаем сохранённый
    payload, ничего не создавая, пока админ не решит по игрокам.
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
        Pure ExternalPlayerLink lookup only — no nickname guessing here (see
        auto_link_by_nickname for that), so this stays safe to call read-only
        from the admin queue page just to render current status.
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

    @staticmethod
    def auto_link_by_nickname(unmatched: List[dict]) -> tuple[Dict[int, Player], List[dict]]:
        """
        Second pass over whatever match_players() couldn't resolve via an
        existing link: try an exact, transliteration/case-normalized nickname
        match (same normalize_for_match() that already guards against
        "Virus"/"Вирус"-style duplicate players on manual creation).
        Auto-links ONLY when exactly one club player matches — zero matches
        (genuinely new person) or 2+ matches (ambiguous nickname, e.g. two
        different people both going by "Тень") still fall through to the
        manual review queue rather than guessing. A successful auto-match
        immediately persists an ExternalPlayerLink, so this only ever runs
        once per external player.
        """
        from app.services.player_search_service import PlayerSearchService

        newly_matched: Dict[int, Player] = {}
        still_unmatched: List[dict] = []
        for p in unmatched:
            candidates = PlayerSearchService.find_exact_duplicates(p["nickname"])
            if len(candidates) == 1:
                player = candidates[0]
                db.session.add(ExternalPlayerLink(
                    source=SOURCE, external_id=p["external_id"],
                    nickname_hint=p["nickname"], player_id=player.id,
                ))
                newly_matched[p["seat"]] = player
            else:
                still_unmatched.append(p)
        if newly_matched:
            db.session.flush()
        return newly_matched, still_unmatched

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
        players_payload = payload.get("players") or []

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

    # ── Corrected re-send of an already-imported game ────────────────────────

    @staticmethod
    def update_existing_game(game: Game, payload: dict) -> tuple[Optional[Game], Optional[str]]:
        """
        A repeated webhook for an external_id that's already "imported" means
        MafiaSpace corrected the protocol (e.g. a role/result mistake caught
        after the fact) — updates the SAME Game in place via
        EditGameOrchestrator (the same undo/redo-ELO pipeline the admin's own
        "edit a finished game" form uses), rather than creating a duplicate.

        Scope: only touches role/win_side/PU/played_at on the EXISTING slots
        by seat number — does not reassign who's seated where. A correction
        that changes the actual roster (not just judging particulars) isn't
        expected from a "protocol fix" and would need a real re-import.
        """
        players_payload = payload.get("players") or []
        slots_by_seat: Dict[int, GameSlot] = {s.seat_number: s for s in game.slots}

        for p in players_payload:
            slot = slots_by_seat.get(p["seat"])
            if not slot:
                continue
            try:
                slot.role = Role(p["role"])
            except ValueError:
                return None, f"Неизвестная роль «{p.get('role')}» на месте {p['seat']}."

        role_values = [s.role.value for s in game.slots]
        if all(v == "civilian" for v in role_values):
            return None, "Все роли — мирный, протокол выглядит некорректным."
        if role_values.count("mafia") + role_values.count("don") == 0:
            return None, "В протоколе нет ни одной роли мафии/дона."

        for s in game.slots:
            s.is_pu = False
            s.pu_mafia_count = 0
        ExternalGameImportService._compute_pu(slots_by_seat, payload)

        winner = (payload.get("winner") or "none").lower()
        game.win_side = _WINNER_MAP.get(winner, WinSide.NONE)

        played_at = payload.get("played_at")
        if played_at:
            game.played_at = _parse_played_at(played_at)

        old_player_ids = [s.player_id for s in game.slots]
        db.session.flush()

        from app.services.orchestrator import EditGameOrchestrator
        EditGameOrchestrator.run(game, old_player_ids, game.tournament_id, game.stage_id)
        return game, None

    # ── Webhook entry point ──────────────────────────────────────────────────

    @staticmethod
    def ingest_webhook_payload(payload: dict) -> ImportOutcome:
        external_id = payload.get("external_id")
        if not external_id:
            return ImportOutcome(ok=False, message="external_id обязателен.")

        players_payload = payload.get("players")
        if not isinstance(players_payload, list) or len(players_payload) != 10:
            return ImportOutcome(ok=False, message="players должен быть списком из 10 игроков.")
        required_keys = ("seat", "external_id", "nickname", "role")
        for p in players_payload:
            if not isinstance(p, dict) or not all(k in p for k in required_keys):
                return ImportOutcome(ok=False, message="Каждый игрок должен содержать seat/external_id/nickname/role.")

        existing = ExternalGameImportService.get_existing_import(external_id)
        if existing:
            if existing.status == "imported" and existing.game:
                # Повторный вебхук с тем же external_id — это исправленный
                # протокол той же игры. Обновляем её на месте вместо второй
                # копии (EditGameOrchestrator корректно откатывает/переигрывает
                # ELO — тот же механизм, что и ручное редактирование игры).
                game, error = ExternalGameImportService.update_existing_game(existing.game, payload)
                if error:
                    return ImportOutcome(ok=False, message=error)
                existing.raw_payload = json.dumps(payload, ensure_ascii=False)
                existing.resolved_at = datetime.now(timezone.utc)
                db.session.commit()
                return ImportOutcome(ok=True, message="Игра обновлена по исправленному протоколу.", import_row=existing, game=game)

            # pending_review (ещё не решено админом) или rejected (админ
            # осознанно отклонил) — не пересоздаём и не трогаем, просто
            # обновляем сохранённый пейлоад на случай, если админ ещё не
            # успел рассмотреть исходный.
            if existing.status == "pending_review":
                existing.raw_payload = json.dumps(payload, ensure_ascii=False)
                db.session.commit()
            return ImportOutcome(ok=True, message="Уже обработано ранее.", import_row=existing, game=existing.game)

        matched, unmatched = ExternalGameImportService.match_players(players_payload)
        if unmatched:
            auto_matched, unmatched = ExternalGameImportService.auto_link_by_nickname(unmatched)
            matched.update(auto_matched)

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
