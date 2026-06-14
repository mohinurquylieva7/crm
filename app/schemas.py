from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─── AUTH ─────────────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── CUSTOMER ────────────────────────────────────────────────────────────────
class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = "lead"
    source: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None


class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── DEAL ─────────────────────────────────────────────────────────────────────
class DealBase(BaseModel):
    title: str
    value: Optional[float] = 0.0
    stage: Optional[str] = "new"
    probability: Optional[int] = 50
    close_date: Optional[datetime] = None
    notes: Optional[str] = None
    customer_id: Optional[int] = None


class DealCreate(DealBase):
    pass


class DealUpdate(DealBase):
    title: Optional[str] = None


class Deal(DealBase):
    id: int
    created_at: datetime
    updated_at: datetime
    customer: Optional[Customer] = None

    class Config:
        from_attributes = True


# ─── TASK ─────────────────────────────────────────────────────────────────────
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None
    customer_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: Optional[str] = None


class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    customer: Optional[Customer] = None

    class Config:
        from_attributes = True


# ─── ACTIVITY ─────────────────────────────────────────────────────────────────
class ActivityBase(BaseModel):
    type: str
    description: Optional[str] = None
    customer_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int
    created_at: datetime
    customer: Optional[Customer] = None

    class Config:
        from_attributes = True
