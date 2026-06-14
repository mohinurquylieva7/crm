import enum
import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Date, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"


class PaymentStatus(str, enum.Enum):
    paid = "paid"
    partial = "partial"
    pending = "pending"
    overdue = "overdue"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    month: Mapped[str | None] = mapped_column(String(20), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod), default=PaymentMethod.cash, nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus), default=PaymentStatus.paid, nullable=False
    )
    received_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
