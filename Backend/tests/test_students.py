import pytest
from datetime import date
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

STUDENT_PAYLOAD = {
    "first_name": "Sardor",
    "last_name": "Testov",
    "phone": "+998901234567",
    "parent_phone": "+998901234500",
    "parent_name": "Testov A.",
    "address": "Toshkent",
    "birth_date": "2006-04-15",
    "enrolled_date": "2024-05-01",
    "status": "active",
    "group_ids": [],
}


class TestStudentsCRUD:
    async def test_list_students(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/students/")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_create_student(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/v1/students/", json=STUDENT_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["first_name"] == "Sardor"
        assert data["last_name"] == "Testov"
        assert data["balance"] == 0
        assert "id" in data

    async def test_get_student(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/v1/students/", json=STUDENT_PAYLOAD)
        student_id = create_resp.json()["id"]

        resp = await auth_client.get(f"/api/v1/students/{student_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == student_id

    async def test_get_student_not_found(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/students/00000000-0000-0000-9999-000000000000")
        assert resp.status_code == 404

    async def test_update_student(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/v1/students/", json=STUDENT_PAYLOAD)
        student_id = create_resp.json()["id"]

        resp = await auth_client.put(f"/api/v1/students/{student_id}", json={
            "first_name": "Sardorbek",
            "status": "inactive",
        })
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Sardorbek"
        assert resp.json()["status"] == "inactive"

    async def test_delete_student(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/v1/students/", json=STUDENT_PAYLOAD)
        student_id = create_resp.json()["id"]

        resp = await auth_client.delete(f"/api/v1/students/{student_id}")
        assert resp.status_code == 204

        get_resp = await auth_client.get(f"/api/v1/students/{student_id}")
        assert get_resp.status_code == 404

    async def test_list_students_search(self, auth_client: AsyncClient):
        await auth_client.post("/api/v1/students/", json={**STUDENT_PAYLOAD, "first_name": "UniqueNameXYZ"})

        resp = await auth_client.get("/api/v1/students/", params={"search": "UniqueNameXYZ"})
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert any(s["first_name"] == "UniqueNameXYZ" for s in items)

    async def test_list_students_pagination(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/students/", params={"page": 1, "size": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2
        assert data["size"] == 2

    async def test_create_student_no_auth(self, client: AsyncClient):
        resp = await client.post("/api/v1/students/", json=STUDENT_PAYLOAD)
        assert resp.status_code == 401
