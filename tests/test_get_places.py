from unittest.mock import patch

import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_get_all_place_success():
    async with AsyncClient(app=app, base_url="http://test") as client:

        response = await client.get("/api/places")

        assert response.status_code == 200
        places = response.json()
        assert len(places) > 0
        assert places[0]["title"] == "Hostel hosted by Eichi"
        #assert response.json()["email"] == "testuser@test.com"


@pytest.mark.asyncio
async def test_get_all_place_failed():
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("main.places_collection.find", side_effect=Exception("Simulated error")):
            response = await client.get("/api/places")
            print(response.content)
        assert response.status_code == 500

        assert response.json()["error"] == "Simulated error"
