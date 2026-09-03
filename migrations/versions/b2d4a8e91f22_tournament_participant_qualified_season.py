"""Add tournament_participants.qualified_via_season_id

Revision ID: b2d4a8e91f22
Revises: a1c9f3d7e001
Create Date: 2026-09-04

Provenance marker for "Стол года" auto-qualification (see
SeasonService._sync_year_tournament_participants /
SeasonService.compute_year_qualifiers). NULL (the default, and the value
for every pre-existing row) means "this registration is NOT an automatic
season-qualifier row" — i.e. a normal manual registration, or a player who
was seated in a tournament game and got auto-registered via
games.py::_ensure_tournament_participants. A non-NULL value means "this row
was added by the year-tournament sync because this player qualified via
that Season" — only rows carrying this marker may ever be removed by a
later re-sync; every other TournamentParticipant row is left untouched no
matter what a re-sync computes.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2d4a8e91f22"
down_revision = "a1c9f3d7e001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tournament_participants",
        sa.Column("qualified_via_season_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_tournament_participants_qualified_via_season",
        "tournament_participants",
        "seasons",
        ["qualified_via_season_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint(
        "fk_tournament_participants_qualified_via_season",
        "tournament_participants",
        type_="foreignkey",
    )
    op.drop_column("tournament_participants", "qualified_via_season_id")
