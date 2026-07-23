from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert "backend" in data


def test_generate_with_mock_backend(monkeypatch):
    monkeypatch.setenv("IMAGE_BACKEND", "mock")

    payload = {
        "product_description": "Premium black wireless headphones",
        "style": "commercial e-commerce",
        "background": "clean studio background",
        "lighting": "soft diffused lighting",
        "camera_angle": "three-quarter product view",
        "aspect_ratio": "1:1",
        "extra_details": "realistic reflections",
        "seed": 42,
        "steps": 8,
        "cfg": 1,
        "width": 768,
        "height": 768,
        "image_count": 1,
    }

    response = client.post(
        "/generate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_description"] == payload["product_description"]
    assert data["seed"] == 42
    assert data["status"] == "mock_generation_complete"
    assert data["backend"].startswith("mock:")
    assert data["images"] == []
    assert data["generation_time"] >= 0
    assert "id" in data


def test_generate_rejects_short_product_description(monkeypatch):
    monkeypatch.setenv("IMAGE_BACKEND", "mock")

    payload = {
        "product_description": "AI",
    }

    response = client.post(
        "/generate",
        json=payload,
    )

    assert response.status_code == 422
