import pytest
import os
import requests


@pytest.mark.asyncio
async def test_upload_photo_successful():
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
        assert len(uploaded_files) == 1
        uploaded_file = uploaded_files[0]
        assert isinstance(uploaded_file, str)
        assert uploaded_file.startswith("photo") and uploaded_file.endswith(".jpg")

@pytest.mark.asyncio
async def test_upload_photo_failed():
    test_folder = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(test_folder, "file.txt")

    with open(file_path, "rb") as file:
        # Create a multipart form request
        files = {"photos": (file.name, file, "image/jpeg")}

        # Send the request
        response = requests.post("http://localhost:8000/api/upload", files=files)

        # Check the response
        assert response.status_code == 400
        uploaded_files = response.json()
        assert response.json()["error"] == f"Please upload a photo"