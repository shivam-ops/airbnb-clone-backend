from unittest.mock import patch

import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_register_valid_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        valid_user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        }

        response = await client.post("/api/register", json=valid_user_data)

        assert response.status_code == 201
        assert response.json() == {"message": "User registered successfully"}


@pytest.mark.asyncio
async def test_already_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        }

        response = await client.post("/api/register", json=user_data)

        assert response.status_code == 400
        assert response.json() == {"detail": "Email already registered"}


@pytest.mark.asyncio
async def test_register_not_successful():
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "name": "John Doe",
            "email": "johnd@example.com",
            "password": "password123"
        }

        with patch("main.users_collection.insert_one", side_effect=Exception):
            response = await client.post("/api/register", json=user_data)
        print(response.content)
        assert response.status_code == 500
        assert response.json()["detail"] == "Error occurred during registration"
