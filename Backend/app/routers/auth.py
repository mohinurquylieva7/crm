from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshRequest, RefreshResponse,
    UserOut, ChangePasswordRequest,
)
from app.services.auth_service import (
    verify_password, create_access_token, create_refresh_token,
    hash_token, hash_password,
)
from app.dependencies import get_current_active_user
from app.config import settings

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Email yoki parol noto'g'ri")
    if not user.is_active:
        raise HTTPException(403, "Hisob faol emas")

    access_token = create_access_token(str(user.id), user.role.value)
    raw_refresh, hashed_refresh = create_refresh_token()

    token_obj = RefreshToken(
        token_hash=hashed_refresh,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(token_obj)
    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    token_obj = result.scalar_one_or_none()

    if not token_obj or token_obj.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(401, "Refresh token yaroqsiz yoki muddati o'tgan")

    user = await db.get(User, token_obj.user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "Foydalanuvchi topilmadi yoki faol emas")

    access_token = create_access_token(str(user.id), user.role.value)
    return RefreshResponse(access_token=access_token)


@router.post("/logout", status_code=204)
async def logout(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token_obj = result.scalar_one_or_none()
    if token_obj:
        token_obj.revoked = True
        await db.commit()


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return UserOut.model_validate(current_user)


@router.put("/me/password", status_code=204)
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.services.auth_service import verify_password as vp
    if not vp(data.old_password, current_user.hashed_password):
        raise HTTPException(400, "Eski parol noto'g'ri")
    current_user.hashed_password = hash_password(data.new_password)
    await db.commit()
