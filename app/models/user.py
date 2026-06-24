import uuid
from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    telegram_chat_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        unique=True,
        index=True,
    )
    bot_token: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    receipts = relationship("Receipt", back_populates="user", cascade="all, delete-orphan")