"""add_is_admin_to_user

Revision ID: 8b5c07e650dc
Revises: 720a2907e35f
Create Date: 2025-12-16 20:26:23.422522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b5c07e650dc'
down_revision: Union[str, None] = '720a2907e35f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_admin column to user table
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove is_admin column from user table
    op.drop_column('user', 'is_admin')
