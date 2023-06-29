from unittest.mock import patch

import jwt.exceptions
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_get_all_bookings_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTMxMTh9.jJxTikRqnvhgoppMGGyqBpL7giK5w0ae4jHSgkOpR-I"
        headers = {"Cookie": f"access_token={access_token}"}
        response = await client.get("/api/bookings", headers=headers)

        assert response.status_code == 200
        places = response.json()
        assert len(places) > 0
        #assert places[0]["title"] == "Hostel hosted by Eichi"
        assert places[0]["name"] == "testUser"


@pytest.mark.asyncio
async def test_get_all_booking_failed():
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("main.bookings_collection.find", side_effect=jwt.exceptions.PyJWTError):
            access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTMxMTh9.jJxTikRqnvhgoppMGGyqBpL7giK5w0ae4jHSgkOpR-I"
            headers = {"Cookie": f"access_token={access_token}"}
            response = await client.get("/api/bookings", headers=headers)
            print(response.content)
        assert response.status_code == 401

        assert response.json()["detail"] == "Invalid token"
