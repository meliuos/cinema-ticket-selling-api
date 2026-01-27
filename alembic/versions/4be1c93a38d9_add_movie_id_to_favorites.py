"""add_movie_id_to_favorites

Revision ID: 4be1c93a38d9
Revises: 780db4fd4b64
Create Date: 2026-01-27 18:42:34.072259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4be1c93a38d9'
down_revision: Union[str, None] = '780db4fd4b64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add movie_id column to favorite table
    op.add_column('favorite', sa.Column('movie_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'favorite', 'movie', ['movie_id'], ['id'])
    op.create_index(op.f('ix_favorite_movie_id'), 'favorite', ['movie_id'], unique=False)


def downgrade() -> None:
    # Remove movie_id column from favorite table
    op.drop_index(op.f('ix_favorite_movie_id'), table_name='favorite')
    op.drop_constraint(None, 'favorite', type_='foreignkey')
    op.drop_column('favorite', 'movie_id')
