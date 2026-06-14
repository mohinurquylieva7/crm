from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.reports import (
    DashboardStats, RevenueItem, AttendanceStatsItem, TeacherPerformanceItem,
)
from app.services import report_service
from app.dependencies import get_current_active_user

router = APIRouter(tags=["reports"])


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await report_service.get_dashboard_stats(db)


@router.get("/revenue", response_model=list[RevenueItem])
async def revenue_report(
    start_month: str | None = Query(None, description="YYYY-MM"),
    end_month: str | None = Query(None, description="YYYY-MM"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await report_service.get_revenue_report(db, start_month, end_month)


@router.get("/attendance-stats", response_model=list[AttendanceStatsItem])
async def attendance_stats(
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await report_service.get_attendance_stats(db, start_date, end_date)


@router.get("/enrollment", response_model=list[dict])
async def enrollment_report(
    year: int = Query(default=2024),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await report_service.get_enrollment_report(db, year)


@router.get("/teacher-performance", response_model=list[TeacherPerformanceItem])
async def teacher_performance(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await report_service.get_teacher_performance(db)
