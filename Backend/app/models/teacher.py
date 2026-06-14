import enum
import uuid
from datetime import date
from sqlalchemy import String, Integer, Float, Date, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from app.models.mixins import TimestampMixin


class TeacherStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class SalaryType(str, enum.Enum):
    fixed = "fixed"
    percent = "percent"


class Teacher(TimestampMixin, Base):
    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    subjects: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    salary: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    salary_type: Mapped[SalaryType] = mapped_column(
        SAEnum(SalaryType), default=SalaryType.fixed, nullable=False
    )
    salary_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    joined_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[TeacherStatus] = mapped_column(
        SAEnum(TeacherStatus), default=TeacherStatus.active, nullable=False
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
