import pytest
import json
from bson.objectid import ObjectId
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app, places_collection


@pytest.mark.asyncio
async def test_get_place_by_id_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_id = '649147f00aee2009d5ff4c3a'

        response = await client.get(f"/api/places/{place_id}")

        assert response.status_code == 200

        response_json = response.json()
        assert response_json["_id"] == place_id


@pytest.mark.asyncio
async def test_get_place_by_id_failed():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_id = '648c295a6bba492162d48fb7'

        response = await client.get(f"/api/places/{place_id}")

        assert response.status_code == 404

        response_json = response.json()
        assert response_json["detail"] == "Place not found"
