import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_get_user_places_authenticated():
    async with AsyncClient(app=app, base_url="http://test") as client:
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTMxMTh9.jJxTikRqnvhgoppMGGyqBpL7giK5w0ae4jHSgkOpR-I"
        headers = {"Cookie": f"access_token={access_token}"}

        response = await client.get("/api/user_places", headers=headers)

        assert response.status_code == 200

        places = response.json()
        assert len(places) > 0

        chosen_place = places[0]
        assert chosen_place["title"] == "Test"


@pytest.mark.asyncio
async def test_get_profile_unauthenticated():
    async with AsyncClient(app=app, base_url="http://test") as client:
        access_token = "asdf"
        headers = {"Cookie": f"access_token={access_token}"}

        response = await client.get("/api/user_places", headers=headers)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"
