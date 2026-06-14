from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.teacher import TeacherStatus, SalaryType


class TeacherBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    subjects: list[str] = []
    salary: int = 0
    salary_type: SalaryType = SalaryType.fixed
    salary_percent: Optional[float] = None
    joined_date: Optional[date] = None
    status: TeacherStatus = TeacherStatus.active
    bio: Optional[str] = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    subjects: Optional[list[str]] = None
    salary: Optional[int] = None
    salary_type: Optional[SalaryType] = None
    salary_percent: Optional[float] = None
    joined_date: Optional[date] = None
    status: Optional[TeacherStatus] = None
    bio: Optional[str] = None


class TeacherOut(TeacherBase):
    id: UUID
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
