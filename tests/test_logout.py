from unittest.mock import patch

import jwt
import pytest
from httpx import AsyncClient
from jwt import PyJWTError

from main import app


@pytest.mark.asyncio
async def test_logout_authenticated():
    async with AsyncClient(app=app, base_url="http://test") as client:
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3R1c2VyQHRlc3QuY29tIiwiaWQiOiI2NDkyYjI5OGIwMDZjZTk5MDY2MTcwZTkiLCJpYXQiOjE2ODc0OTMxMTh9.jJxTikRqnvhgoppMGGyqBpL7giK5w0ae4jHSgkOpR-I"
        headers = {"Cookie": f"access_token={access_token}"}

        response = await client.post("/api/logout", headers=headers)

        assert response.status_code == 204
        assert not response.cookies


# @pytest.mark.asyncio
# async def test_logout_unauthenticated():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         access_token = "invalid_token"
#         headers = {"Cookie": f"access_token={access_token}"}
#
#         with patch.object(jwt, "decode", side_effect=PyJWTError("Invalid token")):
#             response = await client.post("/api/logout", headers=headers)
#
#         assert response.status_code == 401
#         assert response.json()["detail"] == "Invalid token"
