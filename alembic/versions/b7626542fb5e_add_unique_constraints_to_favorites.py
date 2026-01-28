"""add_unique_constraints_to_favorites

Revision ID: b7626542fb5e
Revises: 9f57f4d002d9
Create Date: 2026-01-27 19:12:11.207512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7626542fb5e'
down_revision: Union[str, None] = '9f57f4d002d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraints to prevent duplicate favorites
    op.create_index('ix_favorite_user_cinema_unique', 'favorite', ['user_id', 'cinema_id'], unique=True, postgresql_where=sa.text('cinema_id IS NOT NULL'))
    op.create_index('ix_favorite_user_movie_unique', 'favorite', ['user_id', 'movie_id'], unique=True, postgresql_where=sa.text('movie_id IS NOT NULL'))


def downgrade() -> None:
    # Remove unique constraints
    op.drop_index('ix_favorite_user_movie_unique', table_name='favorite')
    op.drop_index('ix_favorite_user_cinema_unique', table_name='favorite')
