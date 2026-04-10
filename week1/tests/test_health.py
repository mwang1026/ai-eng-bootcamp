import httpx
import pytest

from app.main import app


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


async def test_health_returns_200(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


async def test_health_timestamp_is_iso_format(client):
    from datetime import datetime

    response = await client.get("/health")
    data = response.json()
    # Should parse without error
    datetime.fromisoformat(data["timestamp"])
