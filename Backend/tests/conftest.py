import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import get_db, Base

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/educrm_test"


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    TestSession = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with TestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_engine):
    TestSession = async_sessionmaker(bind=db_engine, expire_on_commit=False)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client, db_engine):
    """Admin token bilan autentifikatsiya qilingan client."""
    from app.database import AsyncSessionLocal
    from app.models.user import User, UserRole
    from app.services.auth_service import hash_password
    from uuid import uuid4

    TestSession = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with TestSession() as session:
        admin = User(
            id=uuid4(),
            email="testadmin@educrm.uz",
            hashed_password=hash_password("TestAdmin1!"),
            full_name="Test Admin",
            role=UserRole.superadmin,
            is_active=True,
        )
        session.add(admin)
        await session.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "email": "testadmin@educrm.uz",
        "password": "TestAdmin1!",
    })
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
