import enum
import uuid
from datetime import date
from sqlalchemy import String, Integer, Date, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from app.models.mixins import TimestampMixin


class GroupStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    completed = "completed"


class Group(TimestampMixin, Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    days: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    start_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    end_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    max_students: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    monthly_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[GroupStatus] = mapped_column(
        SAEnum(GroupStatus), default=GroupStatus.active, nullable=False
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
