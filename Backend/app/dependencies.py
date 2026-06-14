from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import verify_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(401, "Token yaroqsiz")
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(401, "Foydalanuvchi topilmadi")
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_active:
        raise HTTPException(403, "Hisob faol emas")
    return user


def require_roles(*roles: UserRole):
    async def guard(user: User = Depends(get_current_active_user)):
        if user.role not in roles:
            raise HTTPException(403, "Ruxsat yo'q")
        return user
    return guard


# Convenience shortcuts
require_admin = require_roles(UserRole.admin, UserRole.superadmin)
require_teacher = require_roles(UserRole.teacher, UserRole.admin, UserRole.superadmin)
