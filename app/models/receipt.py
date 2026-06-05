import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    total_sum: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )

    qr_raw_data: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )

    user = relationship("User", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")