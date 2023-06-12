from __future__ import annotations

from fastapi import status
from fastapi.testclient import TestClient


def test_health_check(client: TestClient, API_V1_STR: str) -> None:
    """
    GIVEN
    WHEN health check endpoint is called with GET method
    THEN response with status 200 and body OK is returned
    """
    response = client.get(f"{API_V1_STR}/health-check/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "OK"}
