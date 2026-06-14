from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentBase(BaseModel):
    student_id: UUID
    group_id: UUID
    amount: int
    discount: int = 0
    date: date
    month: Optional[str] = None
    year: Optional[int] = None
    method: PaymentMethod = PaymentMethod.cash
    status: PaymentStatus = PaymentStatus.paid
    received_by: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentOut(PaymentBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
