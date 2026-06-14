from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.payment import Payment
from app.models.student import Student
from app.models.group import Group
from app.schemas.payment import PaymentCreate
from app.exceptions import NotFoundError


async def get_payments(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    student_id: UUID | None = None,
    group_id: UUID | None = None,
    month: str | None = None,
    year: int | None = None,
    status: str | None = None,
    method: str | None = None,
) -> tuple[list[Payment], int]:
    query = select(Payment)

    if student_id:
        query = query.where(Payment.student_id == student_id)
    if group_id:
        query = query.where(Payment.group_id == group_id)
    if month:
        query = query.where(Payment.month == month)
    if year:
        query = query.where(Payment.year == year)
    if status:
        query = query.where(Payment.status == status)
    if method:
        query = query.where(Payment.method == method)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.order_by(Payment.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_payment(db: AsyncSession, data: PaymentCreate) -> Payment:
    student = await db.get(Student, data.student_id)
    if not student:
        raise NotFoundError("O'quvchi", str(data.student_id))

    group = await db.get(Group, data.group_id)
    if not group:
        raise NotFoundError("Guruh", str(data.group_id))

    payment = Payment(**data.model_dump())
    db.add(payment)

    net_paid = data.amount - data.discount
    student.total_paid += net_paid
    student.balance += net_paid

    if student.balance >= group.monthly_fee:
        student.balance = 0

    await db.commit()
    await db.refresh(payment)
    return payment


async def get_payment(db: AsyncSession, payment_id: UUID) -> Payment:
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise NotFoundError("To'lov", str(payment_id))
    return payment


async def delete_payment(db: AsyncSession, payment_id: UUID) -> None:
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise NotFoundError("To'lov", str(payment_id))

    student = await db.get(Student, payment.student_id)
    if student:
        net_paid = payment.amount - payment.discount
        student.total_paid -= net_paid
        student.balance -= net_paid

    await db.delete(payment)
    await db.commit()
