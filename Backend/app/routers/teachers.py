from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.database import get_db
from app.models.user import User
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherOut
from app.utils.pagination import PaginatedResponse, paginate
from app.services.upload_service import save_file, delete_file
from app.dependencies import get_current_active_user, require_admin
from app.exceptions import NotFoundError

router = APIRouter(tags=["teachers"])


@router.get("/", response_model=PaginatedResponse[TeacherOut])
async def list_teachers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    query = select(Teacher)
    if search:
        term = f"%{search}%"
        query = query.where(
            or_(Teacher.first_name.ilike(term), Teacher.last_name.ilike(term))
        )
    if status:
        query = query.where(Teacher.status == status)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    rows = (await db.execute(query.offset((page - 1) * size).limit(size))).scalars().all()
    return paginate([TeacherOut.model_validate(t) for t in rows], total, page, size)


@router.post("/", response_model=TeacherOut, status_code=201)
async def create_teacher(
    data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return TeacherOut.model_validate(teacher)


@router.get("/{teacher_id}", response_model=TeacherOut)
async def get_teacher(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    teacher = await db.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundError("O'qituvchi", str(teacher_id))
    return TeacherOut.model_validate(teacher)


@router.put("/{teacher_id}", response_model=TeacherOut)
async def update_teacher(
    teacher_id: UUID,
    data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    teacher = await db.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundError("O'qituvchi", str(teacher_id))
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)
    await db.commit()
    await db.refresh(teacher)
    return TeacherOut.model_validate(teacher)


@router.delete("/{teacher_id}", status_code=204)
async def delete_teacher(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    teacher = await db.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundError("O'qituvchi", str(teacher_id))
    await db.delete(teacher)
    await db.commit()


@router.post("/{teacher_id}/avatar")
async def upload_teacher_avatar(
    teacher_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    teacher = await db.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundError("O'qituvchi", str(teacher_id))
    if teacher.avatar:
        await delete_file(teacher.avatar)
    url = await save_file(file, "avatars/teachers")
    teacher.avatar = url
    await db.commit()
    return {"avatar_url": url}


@router.delete("/{teacher_id}/avatar", status_code=204)
async def delete_teacher_avatar(
    teacher_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    teacher = await db.get(Teacher, teacher_id)
    if not teacher:
        raise NotFoundError("O'qituvchi", str(teacher_id))
    if teacher.avatar:
        await delete_file(teacher.avatar)
        teacher.avatar = None
        await db.commit()
