"""
NavigationService
==================
Single source of truth for "where does this take the user back to" for the
games/tournaments/series-tournaments cluster of pages.

Why this exists: a game can belong to nothing, to a plain tournament, or to
one evening of a series tournament (Game.stage_id -> TournamentSeries), and
a tournament itself can be wrapped by a SeriesTournament. Several views
(game detail's "back" link, the new-game page's cancel link, finish/edit/
delete-game redirects) all need the same answer to "given this
tournament_id/stage_id, where's the one logical place to go back to" —
previously each computed it ad hoc and inconsistently (see CLAUDE_TASKS.md
task 4). Centralizing it here means the rule only has to be right once, and
only ever needs tournament_id/stage_id (both server-validated integers
looked up in the DB) — never a client-supplied URL, so there's no open-
redirect surface here by construction.

Zero Flask imports beyond url_for/request are unavoidable here (this is
inherently a routing concern), but no view/template re-derives this logic
itself anymore — they all call into this module.
"""
from __future__ import annotations

from typing import Optional

from flask import url_for

from app import db
from app.models import SeriesTournament, TournamentSeries


class NavigationService:

    @staticmethod
    def tournament_view_url(tournament_id: int) -> str:
        """Canonical "view this tournament" URL — the series-tournament
        interface if this tournament is wrapped by a SeriesTournament,
        otherwise the plain tournament detail page. Series tournaments
        never send the user into the plain tournament UI for their
        primary "open" action (see tournaments/list.html, tournaments/
        detail.html)."""
        st = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()
        if st:
            return url_for("series_tournaments.series_tournament_detail", series_tournament_id=st.id)
        return url_for("tournaments.tournament_detail", tournament_id=tournament_id)

    @staticmethod
    def tournament_leaderboard_url(tournament_id: int) -> str:
        """Same series-awareness as tournament_view_url, for the
        "leaderboard/rating" action specifically."""
        st = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()
        if st:
            return url_for("series_tournaments.leaderboard", series_tournament_id=st.id)
        return url_for("tournaments.leaderboard", tournament_id=tournament_id)

    @staticmethod
    def game_context_url(tournament_id: Optional[int], stage_id: Optional[int]) -> str:
        """Canonical "back"/"return to" target for a game, given its
        tournament/stage context (works both for an existing Game's own
        tournament_id/stage_id, and for the tournament_id/stage_id query
        params on the new-game page before a Game even exists):

        1. If stage_id belongs to a series evening (TournamentSeries) —
           that evening's own page (not the series-tournament wrapper, and
           not the plain tournament UI).
        2. Else if tournament_id is set — that tournament's canonical view
           (series-aware, see tournament_view_url).
        3. Else — the general games list.

        Never trusts a client-supplied URL: both inputs are looked up
        server-side, so there is no open-redirect vector here.
        """
        if stage_id:
            series = db.session.query(TournamentSeries).filter_by(stage_id=stage_id).first()
            if series:
                return url_for(
                    "series_tournaments.series_detail",
                    series_tournament_id=series.series_tournament_id,
                    series_id=series.id,
                )
        if tournament_id:
            return NavigationService.tournament_view_url(tournament_id)
        return url_for("games.list_games")
