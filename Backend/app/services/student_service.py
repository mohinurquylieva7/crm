from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.student import Student, StudentStatus
from app.models.student_group import StudentGroup
from app.schemas.student import StudentCreate, StudentUpdate
from app.exceptions import NotFoundError, ConflictError


async def get_students(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    search: str | None = None,
    status: str | None = None,
    group_id: UUID | None = None,
) -> tuple[list[Student], int]:
    query = select(Student)

    if search:
        term = f"%{search}%"
        query = query.where(
            or_(
                Student.first_name.ilike(term),
                Student.last_name.ilike(term),
                Student.phone.ilike(term),
            )
        )
    if status:
        query = query.where(Student.status == status)
    if group_id:
        query = query.join(StudentGroup, StudentGroup.student_id == Student.id).where(
            StudentGroup.group_id == group_id
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    students = list(result.scalars().all())

    for student in students:
        student.group_ids = await get_student_group_ids(db, student.id)

    return students, total


async def get_student(db: AsyncSession, student_id: UUID) -> Student:
    student = await db.get(Student, student_id)
    if not student:
        raise NotFoundError("O'quvchi", str(student_id))
    student.group_ids = await get_student_group_ids(db, student_id)
    return student


async def get_student_group_ids(db: AsyncSession, student_id: UUID) -> list[UUID]:
    result = await db.execute(
        select(StudentGroup.group_id).where(StudentGroup.student_id == student_id)
    )
    return list(result.scalars().all())


async def create_student(db: AsyncSession, data: StudentCreate) -> Student:
    student = Student(
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        parent_phone=data.parent_phone,
        parent_name=data.parent_name,
        address=data.address,
        birth_date=data.birth_date,
        enrolled_date=data.enrolled_date,
        status=data.status,
        notes=data.notes,
    )
    db.add(student)
    await db.flush()

    for group_id in data.group_ids:
        db.add(StudentGroup(student_id=student.id, group_id=group_id))

    await db.commit()
    await db.refresh(student)
    student.group_ids = await get_student_group_ids(db, student.id)
    return student


async def update_student(db: AsyncSession, student_id: UUID, data: StudentUpdate) -> Student:
    student = await db.get(Student, student_id)
    if not student:
        raise NotFoundError("O'quvchi", str(student_id))

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    await db.commit()
    await db.refresh(student)
    student.group_ids = await get_student_group_ids(db, student_id)
    return student


async def delete_student(db: AsyncSession, student_id: UUID) -> None:
    student = await db.get(Student, student_id)
    if not student:
        raise NotFoundError("O'quvchi", str(student_id))
    await db.delete(student)
    await db.commit()
