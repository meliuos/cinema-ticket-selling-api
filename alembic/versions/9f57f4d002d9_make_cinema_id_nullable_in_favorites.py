"""make_cinema_id_nullable_in_favorites

Revision ID: 9f57f4d002d9
Revises: 4be1c93a38d9
Create Date: 2026-01-27 19:11:36.415892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f57f4d002d9'
down_revision: Union[str, None] = '4be1c93a38d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make cinema_id nullable to allow movie favorites without cinema
    op.alter_column('favorite', 'cinema_id', nullable=True)


def downgrade() -> None:
    # Revert cinema_id to not nullable
    op.alter_column('favorite', 'cinema_id', nullable=False)
