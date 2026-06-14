from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class AttendanceRecordItem(BaseModel):
    studentId: UUID
    status: str  # present | absent | late | excused
    note: Optional[str] = None


class AttendanceCreate(BaseModel):
    group_id: UUID
    date: date
    taken_by: Optional[str] = None
    records: list[AttendanceRecordItem]


class AttendanceRecordOut(BaseModel):
    id: UUID
    group_id: UUID
    date: date
    taken_by: Optional[str] = None
    records: list[dict] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
