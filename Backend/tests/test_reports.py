import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestReports:
    async def test_dashboard(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/reports/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "active_students" in data
        assert "active_groups" in data
        assert "total_revenue_this_month" in data
        assert "debtors_count" in data
        assert "monthly_revenue" in data
        assert "subject_distribution" in data
        assert isinstance(data["recent_payments"], list)
        assert isinstance(data["debtor_students"], list)

    async def test_revenue_report(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/reports/revenue")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_revenue_report_with_range(self, auth_client: AsyncClient):
        resp = await auth_client.get(
            "/api/v1/reports/revenue",
            params={"start_month": "2024-01", "end_month": "2024-06"},
        )
        assert resp.status_code == 200
        for item in resp.json():
            assert "month" in item
            assert "year" in item
            assert "total" in item
            assert "net_total" in item

    async def test_attendance_stats(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/reports/attendance-stats")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_enrollment_report(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/reports/enrollment", params={"year": 2024})
        assert resp.status_code == 200
        for item in resp.json():
            assert "month" in item
            assert "count" in item

    async def test_teacher_performance(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/reports/teacher-performance")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_reports_require_auth(self, client: AsyncClient):
        for endpoint in ["/dashboard", "/revenue", "/attendance-stats", "/enrollment", "/teacher-performance"]:
            resp = await client.get(f"/api/v1/reports{endpoint}")
            assert resp.status_code == 401
