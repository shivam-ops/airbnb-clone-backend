import os
import pytest
import requests
from main import app, places_collection
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_place_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_data = {
            "id": "649554800656c76954472187",
            "title": "ZZZZ",
            "address": "Test Address",
            "photos": [],  # Empty list for now
            "description": "Test description",
            "amenities": ["WiFi", "Parking"],
            "extraInfo": "Extra information",
            "checkIn": 14,
            "checkOut": 12,
            "maxGuests": 2,
            "price": 100
        }

        test_folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(test_folder, "photo.jpg")

        with open(file_path, "rb") as file:
            # Create a multipart form request
            files = {"photos": (file.name, file, "image/jpeg")}

            # Send the request
            response = requests.post("http://localhost:8000/api/upload", files=files)

            # Check the response
            assert response.status_code == 201
            uploaded_files = response.json()
            print(uploaded_files)

        place_data["photos"] = uploaded_files
        print(place_data)
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc3NTAxOTh9.6LHa3ooYAD0aEBIAtAlfpiC13GMJuDg4iyrlRZZ2Gkk"

        response = await client.put("/api/places", json=place_data, cookies={"access_token": access_token})
        print(response.content)
        assert response.status_code == 200
        assert response.json() == "Place updated successfully"


@pytest.mark.asyncio
async def test_update_place_failed():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_data = {
            "id": "649554800656c76954472187",
            "title": "ZZZZ",
            "address": "Test Address",
            "photos": [],  # Empty list for now
            "description": "Test description",
            "amenities": ["WiFi", "Parking"],
            "extraInfo": "Extra information",
            "checkIn": 14,
            "checkOut": 12,
            "maxGuests": 2,
            "price": 100
        }

        test_folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(test_folder, "photo.jpg")

        with open(file_path, "rb") as file:
            # Create a multipart form request
            files = {"photos": (file.name, file, "image/jpeg")}

            # Send the request
            response = requests.post("http://localhost:8000/api/upload", files=files)

            # Check the response
            assert response.status_code == 201
            uploaded_files = response.json()
            print(uploaded_files)

        place_data["photos"] = uploaded_files
        print(place_data)
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNoaXZhbUB0ZXN0LmNvbSIsImlkIjoiNjQ4OTJkMmUzNzU5MzEwNzJlZWFjNmI0IiwiaWF0IjoxNjg3NzUyNzcyfQ.plg3jB6uA8ud9t9k51Jf9-bqzAJnUEinyEuOozMM440"

        response = await client.put("/api/places", json=place_data, cookies={"access_token": access_token})
        print(response.content)
        assert response.status_code == 403
        assert response.json()["detail"] == "Unauthorized"

