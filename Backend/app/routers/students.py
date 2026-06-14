from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.payment import Payment
from app.models.student_group import StudentGroup
from app.models.group import Group
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut
from app.schemas.payment import PaymentOut
from app.schemas.group import GroupOut
from app.utils.pagination import PaginatedResponse, paginate
from app.services import student_service
from app.services.upload_service import save_file, delete_file
from app.dependencies import get_current_active_user, require_admin

router = APIRouter(tags=["students"])


@router.get("/", response_model=PaginatedResponse[StudentOut])
async def list_students(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    group_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    students, total = await student_service.get_students(db, page, size, search, status, group_id)
    items = [StudentOut.model_validate(s) for s in students]
    return paginate(items, total, page, size)


@router.post("/", response_model=StudentOut, status_code=201)
async def create_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    student = await student_service.create_student(db, data)
    return StudentOut.model_validate(student)


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    student = await student_service.get_student(db, student_id)
    return StudentOut.model_validate(student)


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: UUID,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    student = await student_service.update_student(db, student_id, data)
    return StudentOut.model_validate(student)


@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await student_service.delete_student(db, student_id)


@router.get("/{student_id}/payments", response_model=list[PaymentOut])
async def get_student_payments(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Payment).where(Payment.student_id == student_id)
        .order_by(Payment.created_at.desc())
    )
    return [PaymentOut.model_validate(p) for p in result.scalars().all()]


@router.get("/{student_id}/groups", response_model=list[GroupOut])
async def get_student_groups(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Group)
        .join(StudentGroup, StudentGroup.group_id == Group.id)
        .where(StudentGroup.student_id == student_id)
    )
    groups = result.scalars().all()
    out = []
    for g in groups:
        count_res = await db.execute(
            select(StudentGroup).where(StudentGroup.group_id == g.id)
        )
        go = GroupOut.model_validate(g)
        go.student_count = len(count_res.scalars().all())
        out.append(go)
    return out


@router.post("/{student_id}/avatar")
async def upload_student_avatar(
    student_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    student = await student_service.get_student(db, student_id)
    if student.avatar:
        await delete_file(student.avatar)
    url = await save_file(file, "avatars/students")
    student.avatar = url
    await db.commit()
    return {"avatar_url": url}


@router.delete("/{student_id}/avatar", status_code=204)
async def delete_student_avatar(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    student = await student_service.get_student(db, student_id)
    if student.avatar:
        await delete_file(student.avatar)
        student.avatar = None
        await db.commit()
