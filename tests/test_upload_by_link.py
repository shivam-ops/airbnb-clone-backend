import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_upload_by_link():
    async with AsyncClient(app=app, base_url="http://test") as client:
        links = ["https://hatrabbits.com/wp-content/uploads/2017/01/random.jpg"]
        payload = {"link": links}

        response = await client.post("/api/upload-by-link", json=payload)
        assert response.status_code == 201
        assert len(response.json()) == len(links)


@pytest.mark.asyncio
async def test_upload_by_link():
    async with AsyncClient(app=app, base_url="http://test") as client:
        links = "asfdasdf"
        payload = {"link": links}

        response = await client.post("/api/upload-by-link", json=payload)

        print(response.json())
        assert response.status_code == 400
        assert response.json()["error"] == f"unknown url type: '{links}'"
