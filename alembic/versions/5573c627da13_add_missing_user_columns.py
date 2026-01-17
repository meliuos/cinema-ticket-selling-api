"""add_missing_user_columns

Revision ID: 5573c627da13
Revises: 8b5c07e650dc
Create Date: 2025-12-16 20:29:11.973343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5573c627da13'
down_revision: Union[str, None] = '8b5c07e650dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nullable columns
    op.add_column('user', sa.Column('date_of_birth', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('profile_picture_url', sa.String(length=500), nullable=True))
    op.add_column('user', sa.Column('reset_token', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('reset_token_expiry', sa.DateTime(), nullable=True))

    # Add boolean columns with defaults
    op.add_column('user', sa.Column('dark_mode', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('user', sa.Column('newsletter_subscribed', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove all added columns
    op.drop_column('user', 'newsletter_subscribed')
    op.drop_column('user', 'notifications_enabled')
    op.drop_column('user', 'dark_mode')
    op.drop_column('user', 'reset_token_expiry')
    op.drop_column('user', 'reset_token')
    op.drop_column('user', 'profile_picture_url')
    op.drop_column('user', 'date_of_birth')
