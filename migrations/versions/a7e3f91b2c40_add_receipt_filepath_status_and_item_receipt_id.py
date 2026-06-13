"""add receipt filepath status and item receipt_id

Revision ID: a7e3f91b2c40
Revises: 1c8c91ecfc84
Create Date: 2026-06-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a7e3f91b2c40"
down_revision: Union[str, Sequence[str], None] = "1c8c91ecfc84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

receipt_status_enum = sa.Enum(
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    name="receiptstatus",
)


def upgrade() -> None:
    """Upgrade schema."""
    receipt_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "receipts",
        sa.Column("filepath", sa.String(length=500), nullable=False, server_default=""),
    )
    op.add_column(
        "receipts",
        sa.Column(
            "status",
            receipt_status_enum,
            nullable=False,
            server_default="PROCESSING",
        ),
    )
    op.alter_column("receipts", "filepath", server_default=None)
    op.alter_column("receipts", "status", server_default=None)

    op.add_column("receipt_items", sa.Column("receipt_id", sa.UUID(), nullable=False))
    op.create_foreign_key(
        "fk_receipt_items_receipt_id_receipts",
        "receipt_items",
        "receipts",
        ["receipt_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_receipt_items_receipt_id_receipts",
        "receipt_items",
        type_="foreignkey",
    )
    op.drop_column("receipt_items", "receipt_id")
    op.drop_column("receipts", "status")
    op.drop_column("receipts", "filepath")
    receipt_status_enum.drop(op.get_bind(), checkfirst=True)
