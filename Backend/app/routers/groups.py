from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.database import get_db
from app.models.user import User
from app.models.group import Group
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.student_group import StudentGroup
from app.schemas.group import GroupCreate, GroupUpdate, GroupOut, GroupDetailOut
from app.schemas.teacher import TeacherOut
from app.schemas.student import StudentOut
from app.utils.pagination import PaginatedResponse, paginate
from app.dependencies import get_current_active_user, require_admin
from app.exceptions import NotFoundError
from app.services.student_service import get_student_group_ids

router = APIRouter(tags=["groups"])


async def _group_out(db: AsyncSession, group: Group) -> GroupOut:
    count = (await db.execute(
        select(func.count(StudentGroup.student_id)).where(StudentGroup.group_id == group.id)
    )).scalar_one()
    out = GroupOut.model_validate(group)
    out.student_count = count
    return out


@router.get("/", response_model=PaginatedResponse[GroupOut])
async def list_groups(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    teacher_id: UUID | None = None,
    subject: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    query = select(Group)
    if status:
        query = query.where(Group.status == status)
    if teacher_id:
        query = query.where(Group.teacher_id == teacher_id)
    if subject:
        query = query.where(Group.subject.ilike(f"%{subject}%"))

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    rows = (await db.execute(query.offset((page - 1) * size).limit(size))).scalars().all()
    items = [await _group_out(db, g) for g in rows]
    return paginate(items, total, page, size)


@router.post("/", response_model=GroupOut, status_code=201)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    group = Group(**data.model_dump())
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return await _group_out(db, group)


@router.get("/{group_id}", response_model=GroupDetailOut)
async def get_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    group = await db.get(Group, group_id)
    if not group:
        raise NotFoundError("Guruh", str(group_id))

    teacher = None
    if group.teacher_id:
        t = await db.get(Teacher, group.teacher_id)
        if t:
            teacher = TeacherOut.model_validate(t)

    student_rows = (await db.execute(
        select(Student)
        .join(StudentGroup, StudentGroup.student_id == Student.id)
        .where(StudentGroup.group_id == group_id)
    )).scalars().all()

    students = []
    for s in student_rows:
        so = StudentOut.model_validate(s)
        so.group_ids = await get_student_group_ids(db, s.id)
        students.append(so)

    out = GroupDetailOut.model_validate(group)
    out.student_count = len(students)
    out.teacher = teacher
    out.students = students
    return out


@router.put("/{group_id}", response_model=GroupOut)
async def update_group(
    group_id: UUID,
    data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    group = await db.get(Group, group_id)
    if not group:
        raise NotFoundError("Guruh", str(group_id))
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    await db.commit()
    await db.refresh(group)
    return await _group_out(db, group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    group = await db.get(Group, group_id)
    if not group:
        raise NotFoundError("Guruh", str(group_id))
    await db.delete(group)
    await db.commit()


@router.post("/{group_id}/students", response_model=GroupOut)
async def add_students_to_group(
    group_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    group = await db.get(Group, group_id)
    if not group:
        raise NotFoundError("Guruh", str(group_id))

    student_ids = body.get("student_ids", [])
    for sid in student_ids:
        existing = await db.get(StudentGroup, (sid, group_id))
        if not existing:
            db.add(StudentGroup(student_id=sid, group_id=group_id))
    await db.commit()
    return await _group_out(db, group)


@router.delete("/{group_id}/students/{student_id}", status_code=204)
async def remove_student_from_group(
    group_id: UUID,
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    sg = await db.get(StudentGroup, (student_id, group_id))
    if sg:
        await db.delete(sg)
        await db.commit()
