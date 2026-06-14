import enum
import uuid
from datetime import date
from sqlalchemy import String, Integer, Date, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.mixins import TimestampMixin


class StudentStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    graduated = "graduated"
    frozen = "frozen"


class Student(TimestampMixin, Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    enrolled_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[StudentStatus] = mapped_column(
        SAEnum(StudentStatus), default=StudentStatus.active, nullable=False
    )
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_paid: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
