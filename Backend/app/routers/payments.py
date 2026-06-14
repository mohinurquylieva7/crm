from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut
from app.utils.pagination import PaginatedResponse, paginate
from app.services import payment_service
from app.dependencies import get_current_active_user, require_admin

router = APIRouter(tags=["payments"])


@router.get("/", response_model=PaginatedResponse[PaymentOut])
async def list_payments(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    student_id: UUID | None = None,
    group_id: UUID | None = None,
    month: str | None = None,
    year: int | None = None,
    status: str | None = None,
    method: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    payments, total = await payment_service.get_payments(
        db, page, size, student_id, group_id, month, year, status, method
    )
    return paginate([PaymentOut.model_validate(p) for p in payments], total, page, size)


@router.post("/", response_model=PaymentOut, status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    payment = await payment_service.create_payment(db, data)
    return PaymentOut.model_validate(payment)


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    payment = await payment_service.get_payment(db, payment_id)
    return PaymentOut.model_validate(payment)


@router.delete("/{payment_id}", status_code=204)
async def delete_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await payment_service.delete_payment(db, payment_id)
