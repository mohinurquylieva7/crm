from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.homework import HomeworkType


class ResultItem(BaseModel):
    studentId: UUID
    score: Optional[float] = None
    submitted: bool = False
    submittedDate: Optional[date] = None
    feedback: Optional[str] = None


class HomeworkBase(BaseModel):
    group_id: UUID
    teacher_id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    assigned_date: Optional[date] = None
    type: HomeworkType = HomeworkType.homework
    max_score: int = 100


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    assigned_date: Optional[date] = None
    type: Optional[HomeworkType] = None
    max_score: Optional[int] = None


class HomeworkOut(HomeworkBase):
    id: UUID
    results: list[dict] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
