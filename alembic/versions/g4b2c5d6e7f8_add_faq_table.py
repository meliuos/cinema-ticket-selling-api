"""add_faq_table

Revision ID: g4b2c5d6e7f8
Revises: f3a1b2c4d5e6
Create Date: 2026-02-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'g4b2c5d6e7f8'
down_revision: Union[str, None] = 'f3a1b2c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create faq table
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(), nullable=False),
        sa.Column('answer', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop table
    op.drop_table('faqs')