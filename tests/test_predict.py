"""
Prediction endpoint tests.
Uses a small synthetic image to avoid large file commits.
"""
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def create_test_image() -> bytes:
    """Generate a small RGB image for testing."""
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_predict_with_valid_image():
    """Valid JPEG image should return detections (possibly empty)."""
    image_bytes = create_test_image()
    response = client.post(
        "/predict",
        files={"file": ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")}
    )
    # If model is not loaded, we get 503; otherwise 200
    if response.status_code == 503:
        pytest.skip("Model not loaded in this environment")
    
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "detections" in data
    assert isinstance(data["detections"], list)
    assert "inference_time_ms" in data
    assert data["model_version"] == "mock_detector_v1.0.0"

def test_predict_with_invalid_file_type():
    """Non-image file should return 400."""
    response = client.post(
        "/predict",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    )
    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()

def test_predict_with_large_image():
    """Oversized image should return 413."""
    # Create a genuinely large image (>10MB) using random noise (poor JPEG compression)
    import numpy as np
    np.random.seed(42)
    # 4000x4000 RGB with random noise = ~48MB raw, ~15-20MB JPEG
    noise = np.random.randint(0, 255, (4000, 4000, 3), dtype=np.uint8)
    img = Image.fromarray(noise, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    large_bytes = buf.getvalue()
    
    response = client.post(
        "/predict",
        files={"file": ("large.jpg", io.BytesIO(large_bytes), "image/jpeg")}
    )
    # We expect 413, but if model isn't loaded we get 503 first
    if response.status_code == 503:
        pytest.skip("Model not loaded")
    assert response.status_code == 413