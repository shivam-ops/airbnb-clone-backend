import os
from unittest.mock import patch

import pytest
import requests
from main import app, places_collection
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_place():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_data = {
            "title": "Test Place",
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
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTU4NzN9.7K-kuBdvOdkG0y81j-BOp2cFx_dL4HpNvL5pIPOQcdc"

        response = await client.post("/api/places", json=place_data, cookies={"access_token": access_token})
        print(response.content)
        assert response.status_code == 201
        assert "owner" in response.json()
        assert response.json()["title"] == place_data["title"]
        assert response.json()["address"] == place_data["address"]

        created_place = places_collection.find_one({"title": place_data["title"]})
        assert created_place is not None
        assert created_place["title"] == place_data["title"]
        assert created_place["address"] == place_data["address"]


@pytest.mark.asyncio
async def test_check_duplicate_place():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_data = {
            "title": "Test Place",
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

        place_data["photos"] = uploaded_files
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTU4NzN9.7K-kuBdvOdkG0y81j-BOp2cFx_dL4HpNvL5pIPOQcdc"

        response = await client.post("/api/places", json=place_data, cookies={"access_token": access_token})
        assert response.status_code == 400
        assert response.json()["detail"] == "Place already registered"


@pytest.mark.asyncio
async def test_invalid_place_data():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_data = {
            "title": "",
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

        place_data["photos"] = uploaded_files
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTU4NzN9.7K-kuBdvOdkG0y81j-BOp2cFx_dL4HpNvL5pIPOQcdc"

        response = await client.post("/api/places", json=place_data, cookies={"access_token": access_token})
        assert response.status_code == 400
        assert response.json()["detail"] == "Please provide all required fields"


@pytest.mark.asyncio
async def test_register_place_failed():
    async with AsyncClient(app=app, base_url="http://test") as client:
        place_data = {
            "title": "Test Place",
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
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTU4NzN9.7K-kuBdvOdkG0y81j-BOp2cFx_dL4HpNvL5pIPOQcdc"
        with patch("main.places_collection.insert_one", side_effect=Exception):
            response = await client.post("/api/places", json=place_data, cookies={"access_token": access_token})
            print(response.content)
        assert response.status_code == 500
        assert response.json()["detail"] == "Error occurred while registration"
