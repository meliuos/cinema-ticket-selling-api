"""add_partial_unique_index_seat_reservations

Revision ID: 780db4fd4b64
Revises: 10ecadfb6d35
Create Date: 2026-01-26 18:18:10.647124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '780db4fd4b64'
down_revision: Union[str, None] = '10ecadfb6d35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add partial unique index for PostgreSQL optimization
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_seat_reservation_active_unique 
        ON seat_reservation (screening_id, seat_id) 
        WHERE status IN ('active', 'booked');
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_seat_reservation_active_unique;")
