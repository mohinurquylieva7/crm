import enum
import uuid
from datetime import date
from sqlalchemy import String, Integer, Date, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from app.models.mixins import TimestampMixin


class HomeworkType(str, enum.Enum):
    homework = "homework"
    exam = "exam"
    test = "test"
    project = "project"


class Homework(TimestampMixin, Base):
    __tablename__ = "homeworks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    assigned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    type: Mapped[HomeworkType] = mapped_column(
        SAEnum(HomeworkType), default=HomeworkType.homework, nullable=False
    )
    max_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    results: Mapped[list | None] = mapped_column(JSONB, nullable=True)
