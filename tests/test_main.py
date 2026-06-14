import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def get_auth_header():
    """Create a test user directly in DB and return auth header"""
    from app.auth import get_password_hash
    from app.models import User as UserModel

    db = TestingSessionLocal()
    user = db.query(UserModel).filter(UserModel.email == "test@test.com").first()
    if not user:
        user = UserModel(
            full_name="Test User",
            email="test@test.com",
            hashed_password=get_password_hash("test123456"),
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()

    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "test123456",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ═══ AUTH TESTS ═══

def test_login_success():
    headers = get_auth_header()  # creates user
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "test123456",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    get_auth_header()  # ensure user exists
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401


def test_protected_endpoint_without_token():
    response = client.get("/api/customers")
    assert response.status_code == 401


def test_me_endpoint():
    headers = get_auth_header()
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"


# ═══ CUSTOMER TESTS ═══

def test_create_customer():
    headers = get_auth_header()
    response = client.post("/api/customers", json={
        "name": "Test Customer",
        "email": "customer@example.com",
        "phone": "+998901234567",
        "company": "TestCorp",
        "status": "lead",
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Customer"
    assert data["id"] is not None


def test_list_customers():
    headers = get_auth_header()
    client.post("/api/customers", json={"name": "Customer A"}, headers=headers)
    client.post("/api/customers", json={"name": "Customer B"}, headers=headers)
    response = client.get("/api/customers", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_customer():
    headers = get_auth_header()
    r = client.post("/api/customers", json={"name": "Old Name"}, headers=headers)
    cid = r.json()["id"]
    response = client.put(f"/api/customers/{cid}", json={"name": "New Name"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_customer():
    headers = get_auth_header()
    r = client.post("/api/customers", json={"name": "Delete Me"}, headers=headers)
    cid = r.json()["id"]
    response = client.delete(f"/api/customers/{cid}", headers=headers)
    assert response.status_code == 200
    response = client.get(f"/api/customers/{cid}", headers=headers)
    assert response.status_code == 404


def test_search_customers():
    headers = get_auth_header()
    client.post("/api/customers", json={"name": "Alisher", "company": "TechUZ"}, headers=headers)
    client.post("/api/customers", json={"name": "Bobur", "company": "LogiCo"}, headers=headers)
    response = client.get("/api/customers?search=tech", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


# ═══ DEAL TESTS ═══

def test_create_deal():
    headers = get_auth_header()
    response = client.post("/api/deals", json={
        "title": "Big Deal",
        "value": 15000,
        "stage": "proposal",
        "probability": 60,
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Big Deal"


def test_list_deals_by_stage():
    headers = get_auth_header()
    client.post("/api/deals", json={"title": "Deal 1", "stage": "won"}, headers=headers)
    client.post("/api/deals", json={"title": "Deal 2", "stage": "lost"}, headers=headers)
    response = client.get("/api/deals?stage=won", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_deal():
    headers = get_auth_header()
    r = client.post("/api/deals", json={"title": "Draft"}, headers=headers)
    did = r.json()["id"]
    response = client.put(f"/api/deals/{did}", json={"title": "Final", "stage": "won"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["stage"] == "won"


# ═══ TASK TESTS ═══

def test_create_task():
    headers = get_auth_header()
    response = client.post("/api/tasks", json={
        "title": "Call client",
        "priority": "high",
        "status": "todo",
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["priority"] == "high"


def test_filter_tasks():
    headers = get_auth_header()
    client.post("/api/tasks", json={"title": "Task A", "status": "done"}, headers=headers)
    client.post("/api/tasks", json={"title": "Task B", "status": "todo"}, headers=headers)
    response = client.get("/api/tasks?status=todo", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


# ═══ ACTIVITY TESTS ═══

def test_create_activity():
    headers = get_auth_header()
    response = client.post("/api/activities", json={
        "type": "call",
        "description": "Called the client about proposal",
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["type"] == "call"


# ═══ DASHBOARD TESTS ═══

def test_dashboard_stats():
    headers = get_auth_header()
    client.post("/api/customers", json={"name": "C1"}, headers=headers)
    client.post("/api/deals", json={"title": "D1", "value": 5000, "stage": "won"}, headers=headers)
    client.post("/api/deals", json={"title": "D2", "value": 3000, "stage": "proposal"}, headers=headers)
    client.post("/api/tasks", json={"title": "T1", "status": "todo"}, headers=headers)

    response = client.get("/api/dashboard/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] == 1
    assert data["total_deals"] == 2
    assert data["won_deals"] == 1
    assert data["pipeline_value"] == 3000
    assert data["won_value"] == 5000
    assert data["pending_tasks"] == 1
    assert "pipeline_by_stage" in data
    assert "conversion_rate" in data
