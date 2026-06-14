from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.tenant import TenantSettings
from app.schemas.tenant import TenantSettingsOut, TenantSettingsUpdate
from app.services.upload_service import save_file, delete_file
from app.dependencies import get_current_active_user, require_admin
from app.exceptions import NotFoundError

router = APIRouter(tags=["settings"])


async def _get_or_create_tenant(db: AsyncSession) -> TenantSettings:
    result = await db.execute(select(TenantSettings).limit(1))
    tenant = result.scalar_one_or_none()
    if not tenant:
        tenant = TenantSettings(name="EduCRM")
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
    return tenant


@router.get("/", response_model=TenantSettingsOut)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    tenant = await _get_or_create_tenant(db)
    return TenantSettingsOut.model_validate(tenant)


@router.put("/", response_model=TenantSettingsOut)
async def update_settings(
    data: TenantSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    tenant = await _get_or_create_tenant(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)
    await db.commit()
    await db.refresh(tenant)
    return TenantSettingsOut.model_validate(tenant)


@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    tenant = await _get_or_create_tenant(db)
    if tenant.logo:
        await delete_file(tenant.logo)
    url = await save_file(file, "logos")
    tenant.logo = url
    await db.commit()
    return {"logo_url": url}


@router.delete("/logo", status_code=204)
async def delete_logo(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    tenant = await _get_or_create_tenant(db)
    if tenant.logo:
        await delete_file(tenant.logo)
        tenant.logo = None
        await db.commit()
