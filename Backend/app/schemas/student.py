from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.student import StudentStatus


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_name: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None
    status: StudentStatus = StudentStatus.active
    notes: Optional[str] = None


class StudentCreate(StudentBase):
    enrolled_date: date
    group_ids: list[UUID] = []


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_name: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None
    status: Optional[StudentStatus] = None
    notes: Optional[str] = None


class StudentOut(StudentBase):
    id: UUID
    enrolled_date: date
    balance: int
    total_paid: int
    group_ids: list[UUID] = []
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
