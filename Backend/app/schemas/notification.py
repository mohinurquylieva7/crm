from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    id: UUID
    title: str
    message: str
    type: NotificationType
    is_read: bool
    date: datetime
    link: Optional[str] = None
    user_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)
