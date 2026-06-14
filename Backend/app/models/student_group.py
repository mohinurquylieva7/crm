import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base


class StudentGroup(Base):
    __tablename__ = "student_groups"
    __table_args__ = (
        PrimaryKeyConstraint("student_id", "group_id"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
