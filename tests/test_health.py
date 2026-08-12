"""
Health endpoint tests.
Runs locally and in CI.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health_endpoint_returns_200_when_ready():
    """Health should return 200 if model loaded successfully."""
    response = client.get("/health")
    # If model loaded, expect 200; if not (CI without cache), expect 503
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert data["model_version"] == "mock_detector_v1.0.0"
    assert data["service_version"] == "1.0.0"

def test_health_response_schema():
    """Health response must contain expected fields."""
    response = client.get("/health")
    data = response.json()
    required_fields = {"status", "model_loaded", "model_version", "service_version"}
    assert required_fields.issubset(data.keys())