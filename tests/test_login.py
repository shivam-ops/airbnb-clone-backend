import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "email": "johnxxxx@example.com",
            "password": "password123"
        }

        response = await client.post("/api/login", json=user_data)

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid email or password"}


@pytest.mark.asyncio
async def test_login_successful():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "email": "john@example.com",
            "password": "password123"
        }

        response = await client.post("/api/login", json=user_data)

        assert response.status_code == 200
        assert response.json()["email"] == "john@example.com"
