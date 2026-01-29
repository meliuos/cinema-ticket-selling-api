"""add_movie_notification_table

Revision ID: f3a1b2c4d5e6
Revises: eb3cb25c198e
Create Date: 2026-01-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f3a1b2c4d5e6'
down_revision: Union[str, None] = 'eb3cb25c198e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create movie_notification table
    op.create_table(
        'movie_notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('notified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('notified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['movie_id'], ['movie.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_notification')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_movie_notification_user_id'), 'movie_notification', ['user_id'], unique=False)
    op.create_index(op.f('ix_movie_notification_movie_id'), 'movie_notification', ['movie_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_movie_notification_movie_id'), table_name='movie_notification')
    op.drop_index(op.f('ix_movie_notification_user_id'), table_name='movie_notification')
    
    # Drop table
    op.drop_table('movie_notification')
