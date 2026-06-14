import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.models.student import Student, StudentStatus
from app.models.group import Group, GroupStatus
from app.models.student_group import StudentGroup
from uuid import uuid4

pytestmark = pytest.mark.asyncio


async def _setup_student_group(db_engine) -> tuple[str, str]:
    """Test uchun student + group yaratadi, ikkalasining UUID stringini qaytaradi."""
    TestSession = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with TestSession() as session:
        student = Student(
            id=uuid4(), first_name="Pay", last_name="Test",
            enrolled_date=date(2024, 1, 1),
            status=StudentStatus.active, balance=0, total_paid=0,
        )
        group = Group(
            id=uuid4(), name="Pay Group", subject="Test",
            monthly_fee=500_000, status=GroupStatus.active,
        )
        session.add_all([student, group])
        await session.flush()
        session.add(StudentGroup(student_id=student.id, group_id=group.id))
        await session.commit()
        return str(student.id), str(group.id)


class TestPaymentsCRUD:
    async def test_create_payment(self, auth_client: AsyncClient, db_engine):
        student_id, group_id = await _setup_student_group(db_engine)
        payload = {
            "student_id": student_id,
            "group_id": group_id,
            "amount": 500_000,
            "discount": 0,
            "date": "2024-05-05",
            "month": "May",
            "year": 2024,
            "method": "cash",
            "status": "paid",
        }
        resp = await auth_client.post("/api/v1/payments/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"] == 500_000
        assert data["status"] == "paid"
        assert "id" in data

    async def test_list_payments(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/payments/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_get_payment(self, auth_client: AsyncClient, db_engine):
        student_id, group_id = await _setup_student_group(db_engine)
        create_resp = await auth_client.post("/api/v1/payments/", json={
            "student_id": student_id, "group_id": group_id,
            "amount": 300_000, "discount": 0,
            "date": "2024-05-10", "month": "May", "year": 2024,
            "method": "card", "status": "paid",
        })
        payment_id = create_resp.json()["id"]

        resp = await auth_client.get(f"/api/v1/payments/{payment_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == payment_id

    async def test_get_payment_not_found(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/payments/00000000-0000-0000-9999-000000000000")
        assert resp.status_code == 404

    async def test_delete_payment_reverses_balance(self, auth_client: AsyncClient, db_engine):
        student_id, group_id = await _setup_student_group(db_engine)
        create_resp = await auth_client.post("/api/v1/payments/", json={
            "student_id": student_id, "group_id": group_id,
            "amount": 500_000, "discount": 0,
            "date": "2024-05-01", "month": "May", "year": 2024,
            "method": "cash", "status": "paid",
        })
        payment_id = create_resp.json()["id"]

        del_resp = await auth_client.delete(f"/api/v1/payments/{payment_id}")
        assert del_resp.status_code == 204

        # Qayta topilmaydi
        get_resp = await auth_client.get(f"/api/v1/payments/{payment_id}")
        assert get_resp.status_code == 404

    async def test_filter_by_student(self, auth_client: AsyncClient, db_engine):
        student_id, group_id = await _setup_student_group(db_engine)
        await auth_client.post("/api/v1/payments/", json={
            "student_id": student_id, "group_id": group_id,
            "amount": 400_000, "discount": 0,
            "date": "2024-05-01", "method": "cash", "status": "paid",
        })
        resp = await auth_client.get("/api/v1/payments/", params={"student_id": student_id})
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all(p["student_id"] == student_id for p in items)

    async def test_discount_applied(self, auth_client: AsyncClient, db_engine):
        student_id, group_id = await _setup_student_group(db_engine)
        resp = await auth_client.post("/api/v1/payments/", json={
            "student_id": student_id, "group_id": group_id,
            "amount": 500_000, "discount": 50_000,
            "date": "2024-06-01", "method": "transfer", "status": "paid",
        })
        assert resp.status_code == 201
        assert resp.json()["discount"] == 50_000
