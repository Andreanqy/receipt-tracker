"""rename created_at to operation_time

Revision ID: b8c6a6c30006
Revises: b93f443f4a29
Create Date: 2026-06-15 08:26:58.630476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8c6a6c30006'
down_revision: Union[str, Sequence[str], None] = 'b93f443f4a29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('receipts', 'created_at', new_column_name='operation_time')


def downgrade() -> None:
    op.alter_column('receipts', 'operation_time', new_column_name='created_at')
