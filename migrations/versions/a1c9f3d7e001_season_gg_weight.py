"""Add seasons.gg_weight

Revision ID: a1c9f3d7e001
Revises:
Create Date: 2026-09-04

Fixes the GG weight used by SeasonRatingEngine
(SeasonRating = TotalPoints*WR% + GG*gg_weight) on the Season row itself,
instead of a single global constant. Every season that already exists at
the time this migration runs is backfilled to 0.2 (the historical, still
in-use formula weight) via the column's server_default — existing/closed
seasons' results never change. SeasonService.ensure_year_exists() sets
gg_weight=0.1 explicitly for any season created from now on.

This is the first Alembic revision for this project — there is no earlier
baseline (schema history to date was managed via standalone migrate_*.py
scripts, see migrations/README and the repo root). Safe to run against an
existing production database: it only adds one NOT NULL column with a
server-side default, so every pre-existing row is populated in the same
statement and no data migration step is needed.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1c9f3d7e001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "seasons",
        sa.Column("gg_weight", sa.Float(), nullable=False, server_default="0.2"),
    )


def downgrade():
    op.drop_column("seasons", "gg_weight")
