from unittest.mock import patch

import pytest
from main import app, places_collection
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_booking_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        booking_data = {
            "checkIn": "2023-06-28",
            "checkOut": "2023-06-29",
            "numberOfGuests": 1,
            "name": "testUser",
            "phoneNumber": "121212",
            "place": "649147f00aee2009d5ff4c3a",
            "user": "6492b298b006ce99066170e9",
            "price": 120
        }

        response = await client.post("/api/bookings", json=booking_data)
        print(response.content)
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_booking_failed():
    async with AsyncClient(app=app, base_url="http://test") as client:
        booking_data = {
            "checkIn": "2023-06-28",
            "checkOut": "2023-06-29",
            "numberOfGuests": 1,
            "name": "testUser",
            "phoneNumber": "121212",
            "place": "649147f00aee2009d5ff4c3a",
            "user": "6492b298b006ce99066170e9",
            "price": 120
        }
        with patch("main.bookings_collection.insert_one", side_effect=Exception):
            response = await client.post("/api/bookings", json=booking_data)
            print(response.content)
        assert response.status_code == 500

        assert response.json()["detail"] == "Error occurred while making a booking"


@pytest.mark.asyncio
async def test_same_booking():
    async with AsyncClient(app=app, base_url="http://test") as client:
        booking_data = {
            "checkIn": "2023-06-28",
            "checkOut": "2023-06-29",
            "numberOfGuests": 1,
            "name": "testUser",
            "phoneNumber": "121212",
            "place": "649147f00aee2009d5ff4c3a",
            "user": "6492b298b006ce99066170e9",
            "price": 120
        }
        #with patch("main.bookings_collection.insert_one", side_effect=Exception):
        response = await client.post("/api/bookings", json=booking_data)
        print(response.content)
        assert response.status_code == 400

        assert response.json()["detail"] == "Booking already exists"
