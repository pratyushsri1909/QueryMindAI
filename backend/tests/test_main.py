"""Automated tests for QueryMind AI core FastAPI endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_status_code() -> None:
    """Verify that GET / returns HTTP 200 status code."""
    response = client.get("/")
    assert response.status_code == 200


def test_root_welcome_message() -> None:
    """Verify that GET / returns the expected welcome message and payload."""
    response = client.get("/")
    assert response.json() == {
        "message": "Welcome to QueryMind AI",
        "status": "Backend is running",
    }


def test_health_status_code() -> None:
    """Verify that GET /health returns HTTP 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_payload() -> None:
    """Verify that GET /health returns exactly {'status': 'healthy'}."""
    response = client.get("/health")
    assert response.json() == {"status": "healthy"}
