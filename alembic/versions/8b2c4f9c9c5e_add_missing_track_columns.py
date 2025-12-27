"""Add missing track columns

Revision ID: 8b2c4f9c9c5e
Revises: e1d49c3473ec
Create Date: 2025-12-27 03:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8b2c4f9c9c5e"
down_revision: Union[str, Sequence[str], None] = "e1d49c3473ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the columns expected by the Track model/ETL."""
    op.add_column("tracks", sa.Column("popularity", sa.Integer(), nullable=True))
    op.add_column("tracks", sa.Column("duration_ms", sa.Integer(), nullable=True))
    op.add_column("tracks", sa.Column("explicit", sa.Boolean(), nullable=True))
    op.add_column("tracks", sa.Column("energy", sa.Float(), nullable=True))
    op.add_column("tracks", sa.Column("key", sa.Integer(), nullable=True))
    op.add_column("tracks", sa.Column("loudness", sa.Float(), nullable=True))
    op.add_column("tracks", sa.Column("mode", sa.Integer(), nullable=True))
    op.add_column("tracks", sa.Column("speechiness", sa.Float(), nullable=True))
    op.add_column("tracks", sa.Column("acousticness", sa.Float(), nullable=True))
    op.add_column("tracks", sa.Column("instrumentalness", sa.Float(), nullable=True))
    op.add_column("tracks", sa.Column("liveness", sa.Float(), nullable=True))
    op.add_column("tracks", sa.Column("valence", sa.Float(), nullable=True))
    op.add_column("tracks", sa.Column("time_signature", sa.Integer(), nullable=True))
    op.add_column("tracks", sa.Column("track_genre", sa.String(), nullable=True))


def downgrade() -> None:
    """Remove the columns added in upgrade."""
    op.drop_column("tracks", "track_genre")
    op.drop_column("tracks", "time_signature")
    op.drop_column("tracks", "valence")
    op.drop_column("tracks", "liveness")
    op.drop_column("tracks", "instrumentalness")
    op.drop_column("tracks", "acousticness")
    op.drop_column("tracks", "speechiness")
    op.drop_column("tracks", "mode")
    op.drop_column("tracks", "loudness")
    op.drop_column("tracks", "key")
    op.drop_column("tracks", "energy")
    op.drop_column("tracks", "explicit")
    op.drop_column("tracks", "duration_ms")
    op.drop_column("tracks", "popularity")
