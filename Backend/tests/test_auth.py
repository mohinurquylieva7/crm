import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.models.user import User, UserRole
from app.services.auth_service import hash_password
from uuid import uuid4

pytestmark = pytest.mark.asyncio


async def _create_user(db_engine, email: str, password: str, role: UserRole = UserRole.admin) -> dict:
    TestSession = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with TestSession() as session:
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hash_password(password),
            full_name="Test User",
            role=role,
            is_active=True,
        )
        session.add(user)
        await session.commit()
    return {"email": email, "password": password}


class TestLogin:
    async def test_login_success(self, client: AsyncClient, db_engine):
        creds = await _create_user(db_engine, "login_ok@test.com", "Pass1234!")
        resp = await client.post("/api/v1/auth/login", json=creds)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == creds["email"]

    async def test_login_wrong_password(self, client: AsyncClient, db_engine):
        await _create_user(db_engine, "wrongpass@test.com", "Correct1!")
        resp = await client.post("/api/v1/auth/login", json={
            "email": "wrongpass@test.com", "password": "Wrong1!"
        })
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com", "password": "Pass1234!"
        })
        assert resp.status_code == 401

    async def test_login_inactive_user(self, client: AsyncClient, db_engine):
        TestSession = async_sessionmaker(bind=db_engine, expire_on_commit=False)
        async with TestSession() as session:
            user = User(
                id=uuid4(), email="inactive@test.com",
                hashed_password=hash_password("Pass1234!"),
                full_name="Inactive", role=UserRole.admin, is_active=False,
            )
            session.add(user)
            await session.commit()
        resp = await client.post("/api/v1/auth/login", json={
            "email": "inactive@test.com", "password": "Pass1234!"
        })
        assert resp.status_code == 403


class TestRefreshLogout:
    async def test_refresh_token(self, client: AsyncClient, db_engine):
        creds = await _create_user(db_engine, "refresh_user@test.com", "Pass1234!")
        login_resp = await client.post("/api/v1/auth/login", json=creds)
        refresh_token = login_resp.json()["refresh_token"]

        resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_logout(self, client: AsyncClient, db_engine):
        creds = await _create_user(db_engine, "logout_user@test.com", "Pass1234!")
        login_resp = await client.post("/api/v1/auth/login", json=creds)
        data = login_resp.json()
        access = data["access_token"]
        refresh = data["refresh_token"]

        resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh},
            headers={"Authorization": f"Bearer {access}"},
        )
        assert resp.status_code == 204

        # Revoke qilingan token bilan refresh qilish ishlamaydi
        resp2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
        assert resp2.status_code == 401


class TestMe:
    async def test_get_me(self, client: AsyncClient, db_engine):
        creds = await _create_user(db_engine, "me_user@test.com", "Pass1234!")
        login_resp = await client.post("/api/v1/auth/login", json=creds)
        token = login_resp.json()["access_token"]

        resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == creds["email"]

    async def test_get_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401
