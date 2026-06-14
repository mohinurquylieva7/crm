from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import get_db
from app.models.user import User
from app.models.attendance import AttendanceRecord
from app.schemas.attendance import AttendanceCreate, AttendanceRecordOut
from app.dependencies import get_current_active_user, require_teacher
from app.exceptions import NotFoundError

router = APIRouter(tags=["attendance"])


@router.get("/", response_model=list[AttendanceRecordOut])
async def list_attendance(
    group_id: UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    query = select(AttendanceRecord)
    if group_id:
        query = query.where(AttendanceRecord.group_id == group_id)
    if start_date:
        query = query.where(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.where(AttendanceRecord.date <= end_date)
    query = query.order_by(AttendanceRecord.date.desc())
    rows = (await db.execute(query)).scalars().all()
    return [AttendanceRecordOut.model_validate(r) for r in rows]


@router.post("/", response_model=AttendanceRecordOut, status_code=201)
async def upsert_attendance(
    data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_teacher),
):
    existing = (await db.execute(
        select(AttendanceRecord).where(
            AttendanceRecord.group_id == data.group_id,
            AttendanceRecord.date == data.date,
        )
    )).scalar_one_or_none()

    records_data = [r.model_dump() for r in data.records]

    if existing:
        existing.taken_by = data.taken_by
        existing.records = records_data
        await db.commit()
        await db.refresh(existing)
        return AttendanceRecordOut.model_validate(existing)

    record = AttendanceRecord(
        group_id=data.group_id,
        date=data.date,
        taken_by=data.taken_by,
        records=records_data,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return AttendanceRecordOut.model_validate(record)


@router.get("/group/{group_id}/date/{record_date}", response_model=AttendanceRecordOut)
async def get_attendance_by_group_date(
    group_id: UUID,
    record_date: date,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    record = (await db.execute(
        select(AttendanceRecord).where(
            AttendanceRecord.group_id == group_id,
            AttendanceRecord.date == record_date,
        )
    )).scalar_one_or_none()
    if not record:
        raise NotFoundError("Davomat yozuvi")
    return AttendanceRecordOut.model_validate(record)


@router.get("/{record_id}", response_model=AttendanceRecordOut)
async def get_attendance(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    record = await db.get(AttendanceRecord, record_id)
    if not record:
        raise NotFoundError("Davomat yozuvi", str(record_id))
    return AttendanceRecordOut.model_validate(record)
