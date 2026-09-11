from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_recommend_layout_endpoint():
    payload = {
        "package": {
            "package_width_mm": 100.0,
            "package_height_mm": 50.0,
            "printing_area_width_mm": 80.0,
            "printing_area_height_mm": 40.0,
            "printing_area_x_mm": 10.0,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 4,
            "tablet_diameter_mm": 8.0,
            "positions": [
                {"x_mm": 15.0, "y_mm": 10.0},
                {"x_mm": 15.0, "y_mm": 25.0},
                {"x_mm": 30.0, "y_mm": 10.0},
                {"x_mm": 30.0, "y_mm": 25.0},
            ],
        },
        "code": {
            "value": "MED001",
            "code_type": "human-readable",
            "min_size_mm": 15.0,
            "orientation_deg": 0.0,
        },
        "information": {
            "medicine_name": "Paracetamol",
            "strength": "500mg",
        },
        "min_margin_mm": 1.0,
    }

    response = client.post("/api/layouts/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "package" in data
    assert "elements" in data
    assert len(data["elements"]) >= 4
    assert data["validation"] is not None


def test_preview_layout_endpoint():
    payload = {
        "layout": {
            "id": "test_layout",
            "package": {
                "package_width_mm": 80.0,
                "package_height_mm": 40.0,
                "printing_area_width_mm": 70.0,
                "printing_area_height_mm": 30.0,
                "printing_area_x_mm": 5.0,
                "printing_area_y_mm": 5.0,
            },
            "elements": [
                {
                    "id": "text_1",
                    "type": "text",
                    "content": "MED001",
                    "x_mm": 10.0,
                    "y_mm": 10.0,
                    "width_mm": 20.0,
                    "height_mm": 5.0,
                }
            ],
        }
    }

    response = client.post("/api/layouts/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "svg" in data
    assert "validation" in data
    assert data["validation"]["valid"] is True


def test_get_layout_not_found():
    response = client.get("/api/layouts/nonexistent_123")
    assert response.status_code == 404


def test_preview_from_request_endpoint():
    payload = {
        "request": {
            "package": {
                "package_width_mm": 90.0,
                "package_height_mm": 45.0,
                "printing_area_width_mm": 80.0,
                "printing_area_height_mm": 35.0,
                "margin_left_mm": 5.0,
                "margin_top_mm": 5.0,
            },
            "tablet": {
                "tablet_count": 2,
                "tablet_diameter_mm": 8.0,
            },
            "marking": {
                "marking_enabled": True,
                "marking_side": "front",
                "marking_method": "inkjet",
                "code_value": "MED001",
            },
            "code": {
                "code_value": "MED001",
                "code_type": "human-readable",
            },
        }
    }
    response = client.post("/api/layouts/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "svg" in data
    assert "<svg" in data["svg"]
    assert data["validation"]["valid"] is True

