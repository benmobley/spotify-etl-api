"""Initial tracks table with indexes

Revision ID: e1d49c3473ec
Revises: 
Create Date: 2025-11-16 16:39:03.955006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1d49c3473ec'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create tracks table
    op.create_table('tracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_name', sa.String(), nullable=False),
        sa.Column('artist', sa.String(), nullable=False),
        sa.Column('album', sa.String(), nullable=True),
        sa.Column('danceability', sa.Float(), nullable=True),
        sa.Column('tempo', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('idx_tracks_artist', 'tracks', ['artist'])
    op.create_index('idx_tracks_track_name', 'tracks', ['track_name'])
    op.create_index('idx_tracks_danceability', 'tracks', ['danceability'])
    op.create_index('idx_tracks_tempo', 'tracks', ['tempo'])
    
    # Create unique constraint for data integrity
    op.create_unique_constraint('uq_tracks_track_artist_album', 'tracks', 
                               ['track_name', 'artist', 'album'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the table (this will also drop indexes and constraints)
    op.drop_table('tracks')
