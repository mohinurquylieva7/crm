from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.schemas.payment import PaymentOut
from app.schemas.student import StudentOut


class DashboardStats(BaseModel):
    active_students: int
    active_groups: int
    total_revenue_this_month: int
    debtors_count: int
    total_debt: int
    today_attendance_present: int
    today_attendance_total: int
    recent_payments: list[PaymentOut]
    debtor_students: list[StudentOut]
    monthly_revenue: list[dict]
    subject_distribution: list[dict]


class RevenueItem(BaseModel):
    month: str
    year: int
    total: int
    net_total: int
    count: int


class AttendanceStatsItem(BaseModel):
    group_id: UUID
    group_name: str
    teacher_name: str
    total_sessions: int
    present_count: int
    present_pct: float


class TeacherPerformanceItem(BaseModel):
    teacher_id: UUID
    teacher_name: str
    group_count: int
    student_count: int
    revenue: int
    avg_attendance_pct: float


class EnrollmentItem(BaseModel):
    month: int
    year: int
    count: int
