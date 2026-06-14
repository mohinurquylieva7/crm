from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.group import GroupStatus
from app.schemas.teacher import TeacherOut
from app.schemas.student import StudentOut


class GroupBase(BaseModel):
    name: str
    subject: str
    teacher_id: Optional[UUID] = None
    days: list[str] = []
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    max_students: int = 12
    monthly_fee: int
    status: GroupStatus = GroupStatus.active
    start_date: Optional[date] = None
    level: Optional[str] = None
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    teacher_id: Optional[UUID] = None
    days: Optional[list[str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    max_students: Optional[int] = None
    monthly_fee: Optional[int] = None
    status: Optional[GroupStatus] = None
    start_date: Optional[date] = None
    level: Optional[str] = None
    description: Optional[str] = None


class GroupOut(GroupBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    student_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class GroupDetailOut(GroupOut):
    teacher: Optional[TeacherOut] = None
    students: list[StudentOut] = []
