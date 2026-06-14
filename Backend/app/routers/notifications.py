from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationOut
from app.dependencies import get_current_active_user
from app.exceptions import NotFoundError

router = APIRouter(tags=["notifications"])


@router.get("/", response_model=list[NotificationOut])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = (await db.execute(
        select(Notification)
        .where(
            or_(Notification.user_id == current_user.id, Notification.user_id == None)  # noqa: E711
        )
        .order_by(Notification.date.desc())
    )).scalars().all()
    return [NotificationOut.model_validate(n) for n in rows]


@router.put("/{notification_id}/read", status_code=204)
async def mark_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise NotFoundError("Bildirishnoma", str(notification_id))
    notification.is_read = True
    await db.commit()


@router.put("/read-all", status_code=204)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = (await db.execute(
        select(Notification).where(
            or_(Notification.user_id == current_user.id, Notification.user_id == None)  # noqa: E711
        )
    )).scalars().all()
    for n in rows:
        n.is_read = True
    await db.commit()


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise NotFoundError("Bildirishnoma", str(notification_id))
    await db.delete(notification)
    await db.commit()
