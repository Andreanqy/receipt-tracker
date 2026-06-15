import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    receipt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("receipts.id", ondelete="CASCADE"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        default=Decimal("1.000"),
        nullable=False
    )
    sum: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    receipt = relationship("Receipt", back_populates="items")