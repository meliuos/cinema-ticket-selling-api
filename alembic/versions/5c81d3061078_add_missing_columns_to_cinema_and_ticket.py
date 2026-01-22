"""add_missing_columns_to_cinema_and_ticket

Revision ID: 5c81d3061078
Revises: 5573c627da13
Create Date: 2025-12-16 20:32:29.689369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5c81d3061078'
down_revision: Union[str, None] = '5573c627da13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to cinema table
    op.add_column('cinema', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('cinema', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('cinema', sa.Column('imageurl', sa.String(length=500), nullable=True))
    op.add_column('cinema', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('cinema', sa.Column('hasParking', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('cinema', sa.Column('isAccessible', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('cinema', sa.Column('amenities', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Add missing column to ticket table
    op.add_column('ticket', sa.Column('confirmed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove columns from ticket table
    op.drop_column('ticket', 'confirmed_at')

    # Remove columns from cinema table
    op.drop_column('cinema', 'amenities')
    op.drop_column('cinema', 'isAccessible')
    op.drop_column('cinema', 'hasParking')
    op.drop_column('cinema', 'phone')
    op.drop_column('cinema', 'imageurl')
    op.drop_column('cinema', 'latitude')
    op.drop_column('cinema', 'longitude')
