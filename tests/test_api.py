"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"]["model_1_measurement"] is True


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "model_1_benchmarks" in data


def test_fit_check_endpoint():
    payload = {
        "height_cm": 170.0,
        "weight_kg": 70.0,
        "gender": "male",
        "photo_id": "001f3a88501980a5eca6f6346a0ca8d9"
    }
    response = client.post("/api/v1/fit-check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "chest_cm" in data["predictions"]
    assert "waist_cm" in data["predictions"]
    assert "hip_cm" in data["predictions"]


def test_recommend_endpoint():
    payload = {
        "body_measurements": {"chest": 98.0, "waist": 82.0, "hip": 102.0},
        "garment_specs": {"chest": 102.0, "waist": 86.0, "hip": 105.0},
        "fabric_stretch": 0.05
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["fit_category"] in ["Fit", "Small", "Large"]
    assert "primary_ease_cm" in data


def test_color_endpoint():
    payload = {
        "rgb_hex": "#D29B72"
    }
    response = client.post("/api/v1/color-palette", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["undertone"] in ["Warm", "Cool", "Neutral"]
    assert data["season"] in ["Spring", "Summer", "Autumn", "Winter"]
    assert "best_colors" in data["palette"]


def test_chat_endpoint():
    payload = {
        "query": "How many days do I have to return an ill-fitting shirt?"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["response"]) > 0
    assert len(data["citations"]) > 0
