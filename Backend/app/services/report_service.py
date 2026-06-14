from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract, case
from app.models.student import Student, StudentStatus
from app.models.group import Group, GroupStatus
from app.models.payment import Payment
from app.models.attendance import AttendanceRecord
from app.models.teacher import Teacher
from app.models.student_group import StudentGroup
from app.schemas.reports import (
    DashboardStats, RevenueItem, AttendanceStatsItem,
    TeacherPerformanceItem, EnrollmentItem,
)
from app.schemas.payment import PaymentOut
from app.schemas.student import StudentOut


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    today = date.today()
    current_month = today.month
    current_year = today.year

    active_students = (await db.execute(
        select(func.count(Student.id)).where(Student.status == StudentStatus.active)
    )).scalar_one()

    active_groups = (await db.execute(
        select(func.count(Group.id)).where(Group.status == GroupStatus.active)
    )).scalar_one()

    revenue_row = (await db.execute(
        select(func.coalesce(func.sum(Payment.amount - Payment.discount), 0))
        .where(
            extract("month", Payment.date) == current_month,
            extract("year", Payment.date) == current_year,
        )
    )).scalar_one()
    total_revenue_this_month = int(revenue_row)

    debtors = (await db.execute(
        select(Student).where(Student.balance < 0)
    )).scalars().all()
    debtors_count = len(debtors)
    total_debt = abs(sum(s.balance for s in debtors if s.balance < 0))

    attendance_record = (await db.execute(
        select(AttendanceRecord).where(AttendanceRecord.date == today)
    )).scalars().all()
    today_present = 0
    today_total = 0
    for rec in attendance_record:
        records = rec.records or []
        today_total += len(records)
        today_present += sum(1 for r in records if r.get("status") == "present")

    recent_payments_rows = (await db.execute(
        select(Payment).order_by(Payment.created_at.desc()).limit(10)
    )).scalars().all()

    monthly_revenue_rows = (await db.execute(
        select(
            extract("month", Payment.date).label("month"),
            extract("year", Payment.date).label("year"),
            func.sum(Payment.amount - Payment.discount).label("revenue"),
            func.count(Payment.id).label("count"),
        )
        .group_by("month", "year")
        .order_by("year", "month")
        .limit(12)
    )).all()

    monthly_revenue = [
        {"month": int(r.month), "year": int(r.year), "revenue": int(r.revenue or 0), "count": int(r.count)}
        for r in monthly_revenue_rows
    ]

    subject_rows = (await db.execute(
        select(Group.subject, func.count(Group.id).label("count"))
        .where(Group.status == GroupStatus.active)
        .group_by(Group.subject)
    )).all()
    subject_distribution = [{"subject": r.subject, "count": r.count} for r in subject_rows]

    debtor_out = []
    for s in debtors[:10]:
        group_ids_rows = (await db.execute(
            select(StudentGroup.group_id).where(StudentGroup.student_id == s.id)
        )).scalars().all()
        d = StudentOut.model_validate(s)
        d.group_ids = list(group_ids_rows)
        debtor_out.append(d)

    return DashboardStats(
        active_students=active_students,
        active_groups=active_groups,
        total_revenue_this_month=total_revenue_this_month,
        debtors_count=debtors_count,
        total_debt=total_debt,
        today_attendance_present=today_present,
        today_attendance_total=today_total,
        recent_payments=[PaymentOut.model_validate(p) for p in recent_payments_rows],
        debtor_students=debtor_out,
        monthly_revenue=monthly_revenue,
        subject_distribution=subject_distribution,
    )


async def get_revenue_report(
    db: AsyncSession, start_month: str | None, end_month: str | None
) -> list[RevenueItem]:
    query = select(
        extract("year", Payment.date).label("year"),
        extract("month", Payment.date).label("month"),
        func.sum(Payment.amount).label("total"),
        func.sum(Payment.amount - Payment.discount).label("net_total"),
        func.count(Payment.id).label("count"),
    ).group_by("year", "month").order_by("year", "month")

    if start_month:
        y, m = map(int, start_month.split("-"))
        query = query.where(
            (extract("year", Payment.date) > y)
            | ((extract("year", Payment.date) == y) & (extract("month", Payment.date) >= m))
        )
    if end_month:
        y, m = map(int, end_month.split("-"))
        query = query.where(
            (extract("year", Payment.date) < y)
            | ((extract("year", Payment.date) == y) & (extract("month", Payment.date) <= m))
        )

    rows = (await db.execute(query)).all()
    months_uz = ["", "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
                 "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]

    return [
        RevenueItem(
            month=months_uz[int(r.month)],
            year=int(r.year),
            total=int(r.total or 0),
            net_total=int(r.net_total or 0),
            count=int(r.count),
        )
        for r in rows
    ]


async def get_attendance_stats(
    db: AsyncSession, start_date: date | None, end_date: date | None
) -> list[AttendanceStatsItem]:
    query = select(AttendanceRecord)
    if start_date:
        query = query.where(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.where(AttendanceRecord.date <= end_date)

    records = (await db.execute(query)).scalars().all()

    stats: dict = {}
    for rec in records:
        gid = str(rec.group_id)
        if gid not in stats:
            stats[gid] = {"sessions": 0, "present": 0, "total": 0}
        stats[gid]["sessions"] += 1
        for r in (rec.records or []):
            stats[gid]["total"] += 1
            if r.get("status") == "present":
                stats[gid]["present"] += 1

    result = []
    for gid, data in stats.items():
        group = await db.get(Group, gid)
        if not group:
            continue
        teacher_name = ""
        if group.teacher_id:
            teacher = await db.get(Teacher, group.teacher_id)
            if teacher:
                teacher_name = f"{teacher.first_name} {teacher.last_name}"
        pct = (data["present"] / data["total"] * 100) if data["total"] > 0 else 0.0
        result.append(AttendanceStatsItem(
            group_id=group.id,
            group_name=group.name,
            teacher_name=teacher_name,
            total_sessions=data["sessions"],
            present_count=data["present"],
            present_pct=round(pct, 1),
        ))
    return result


async def get_enrollment_report(db: AsyncSession, year: int) -> list[dict]:
    rows = (await db.execute(
        select(
            extract("month", Student.enrolled_date).label("month"),
            func.count(Student.id).label("count"),
        )
        .where(extract("year", Student.enrolled_date) == year)
        .group_by("month")
        .order_by("month")
    )).all()
    return [{"month": int(r.month), "year": year, "count": int(r.count)} for r in rows]


async def get_teacher_performance(db: AsyncSession) -> list[TeacherPerformanceItem]:
    teachers = (await db.execute(select(Teacher))).scalars().all()
    result = []
    for teacher in teachers:
        groups_rows = (await db.execute(
            select(Group).where(Group.teacher_id == teacher.id, Group.status == GroupStatus.active)
        )).scalars().all()
        group_ids = [g.id for g in groups_rows]

        student_count = 0
        if group_ids:
            student_count = (await db.execute(
                select(func.count(StudentGroup.student_id.distinct()))
                .where(StudentGroup.group_id.in_(group_ids))
            )).scalar_one()

        revenue = 0
        if group_ids:
            rev = (await db.execute(
                select(func.coalesce(func.sum(Payment.amount - Payment.discount), 0))
                .where(Payment.group_id.in_(group_ids))
            )).scalar_one()
            revenue = int(rev)

        result.append(TeacherPerformanceItem(
            teacher_id=teacher.id,
            teacher_name=f"{teacher.first_name} {teacher.last_name}",
            group_count=len(group_ids),
            student_count=int(student_count),
            revenue=revenue,
            avg_attendance_pct=0.0,
        ))
    return result
