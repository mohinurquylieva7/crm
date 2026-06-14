from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.homework import Homework
from app.schemas.homework import HomeworkCreate, HomeworkUpdate, HomeworkOut, ResultItem
from app.utils.pagination import PaginatedResponse, paginate
from app.dependencies import get_current_active_user, require_teacher
from app.exceptions import NotFoundError

router = APIRouter(tags=["homework"])


@router.get("/", response_model=PaginatedResponse[HomeworkOut])
async def list_homework(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    group_id: UUID | None = None,
    teacher_id: UUID | None = None,
    type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    query = select(Homework)
    if group_id:
        query = query.where(Homework.group_id == group_id)
    if teacher_id:
        query = query.where(Homework.teacher_id == teacher_id)
    if type:
        query = query.where(Homework.type == type)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    rows = (await db.execute(
        query.order_by(Homework.created_at.desc()).offset((page - 1) * size).limit(size)
    )).scalars().all()
    return paginate([HomeworkOut.model_validate(h) for h in rows], total, page, size)


@router.post("/", response_model=HomeworkOut, status_code=201)
async def create_homework(
    data: HomeworkCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_teacher),
):
    hw = Homework(**data.model_dump())
    db.add(hw)
    await db.commit()
    await db.refresh(hw)
    return HomeworkOut.model_validate(hw)


@router.get("/{homework_id}", response_model=HomeworkOut)
async def get_homework(
    homework_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    hw = await db.get(Homework, homework_id)
    if not hw:
        raise NotFoundError("Vazifa", str(homework_id))
    return HomeworkOut.model_validate(hw)


@router.put("/{homework_id}", response_model=HomeworkOut)
async def update_homework(
    homework_id: UUID,
    data: HomeworkUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_teacher),
):
    hw = await db.get(Homework, homework_id)
    if not hw:
        raise NotFoundError("Vazifa", str(homework_id))
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(hw, field, value)
    await db.commit()
    await db.refresh(hw)
    return HomeworkOut.model_validate(hw)


@router.delete("/{homework_id}", status_code=204)
async def delete_homework(
    homework_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_teacher),
):
    hw = await db.get(Homework, homework_id)
    if not hw:
        raise NotFoundError("Vazifa", str(homework_id))
    await db.delete(hw)
    await db.commit()


@router.put("/{homework_id}/results", response_model=HomeworkOut)
async def update_results(
    homework_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_teacher),
):
    hw = await db.get(Homework, homework_id)
    if not hw:
        raise NotFoundError("Vazifa", str(homework_id))
    hw.results = body.get("results", [])
    await db.commit()
    await db.refresh(hw)
    return HomeworkOut.model_validate(hw)
