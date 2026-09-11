import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_base_payload(opt_target: str = "RECOMMEND") -> dict:
    return {
        "package": {
            "package_width_mm": 130.0,
            "package_height_mm": 65.0,
            "printing_area_width_mm": 110.0,
            "printing_area_height_mm": 55.0,
            "printing_area_x_mm": 10.0,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 6,
            "tablet_diameter_mm": 9.0,
        },
        "code": {
            "value": "MED-INT-001",
            "code_type": "datamatrix",
            "min_size_mm": 12.0,
        },
        "information": {
            "medicine_name": "Amoxicillin",
            "strength": "500 mg",
            "batch": "B2026-X",
            "mfg": "2026-03",
            "exp": "2028-03",
        },
        "constraints": {
            "minimum_margin_mm": 2.0,
            "minimum_element_spacing_mm": 1.5,
        },
        "optimization_target": opt_target,
    }


# 1. Valid recommendation request
def test_valid_recommendation_request():
    payload = get_base_payload()
    response = client.post("/api/layouts/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "package" in data
    assert "elements" in data
    assert len(data["elements"]) >= 7
    assert data["validation"]["valid"] is True


# 2. COST recommendation
def test_cost_recommendation():
    payload = get_base_payload(opt_target="COST")
    response = client.post("/api/layouts/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommended_strategy"] == "COST"
    assert data["cost_efficiency"] is not None
    assert data["cost_efficiency"] > 0.0


# 3. BALANCED recommendation
def test_balanced_recommendation():
    payload = get_base_payload(opt_target="BALANCED")
    response = client.post("/api/layouts/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommended_strategy"] == "BALANCED"
    assert data["balanced_score"] is not None
    assert data["balanced_score"] > 0.0


# 4. ACCESSIBILITY recommendation
def test_accessibility_recommendation():
    payload = get_base_payload(opt_target="ACCESSIBILITY")
    response = client.post("/api/layouts/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommended_strategy"] == "ACCESSIBILITY"
    assert data["accessibility_score"] is not None
    assert data["accessibility_score"] > 0.0


# 5. Full 3-alternative recommendation
def test_full_3_alternative_recommendation():
    payload = get_base_payload(opt_target="RECOMMEND")
    response = client.post("/api/layouts/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommended_strategy"] in ("COST", "BALANCED", "ACCESSIBILITY")
    assert data["recommended_layout"] is not None
    assert "alternatives" in data
    assert len(data["alternatives"]) == 3
    assert data["score"] is not None
    for alt in data["alternatives"]:
        assert alt["strategy"] in ("COST", "BALANCED", "ACCESSIBILITY")
        assert alt["score"] > 0.0
        assert "space_utilization" in alt
        assert "readability" in alt
        assert "print_efficiency" in alt
        assert "cost_efficiency" in alt
        assert "scan_reliability" in alt


# 6. Invalid package dimensions
def test_invalid_package_dimensions():
    # Negative package dimensions
    invalid_payload = get_base_payload()
    invalid_payload["package"]["package_width_mm"] = -10.0
    response = client.post("/api/layouts/recommend", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert len(data["error"]["details"]) > 0


# 7. Impossible layout handling
def test_impossible_layout():
    # Attempting to fit 80 large tablets into an impossibly small package
    impossible_req = {
        "package": {
            "package_width_mm": 25.0,
            "package_height_mm": 20.0,
            "printing_area_width_mm": 15.0,
            "printing_area_height_mm": 12.0,
            "printing_area_x_mm": 5.0,
            "printing_area_y_mm": 4.0,
        },
        "tablet": {
            "tablet_count": 80,
            "tablet_diameter_mm": 12.0,
        },
        "constraints": {
            "minimum_margin_mm": 2.0,
            "minimum_element_spacing_mm": 1.5,
        },
    }

    # 7a. Recommend endpoint returns structured failure
    rec_res = client.post("/api/layouts/recommend", json=impossible_req)
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["success"] is False
    assert len(rec_data["errors"]) > 0
    assert rec_data["recommended_strategy"] is None

    # 7b. Preview endpoint returns structured failure without fake SVG
    prev_res = client.post("/api/layouts/preview", json={"request": impossible_req})
    assert prev_res.status_code == 200
    prev_data = prev_res.json()
    assert prev_data["success"] is False
    assert prev_data["svg"] is None
    assert len(prev_data["errors"]) > 0

    # 7c. PDF endpoint returns HTTP 400 Bad Request without fake PDF
    pdf_res = client.post("/api/layouts/pdf", json={"request": impossible_req})
    assert pdf_res.status_code == 400
    pdf_data = pdf_res.json()
    assert "Layout generation failed" in str(pdf_data)


# 8. SVG preview integration
def test_svg_preview_integration():
    payload = {"request": get_base_payload()}
    response = client.post("/api/layouts/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "svg" in data
    assert data["svg"].startswith("<svg")
    assert data["svg"].strip().endswith("</svg>")
    assert "Amoxicillin" in data["svg"]
    assert "data-shape" in data["svg"]


# 9. PDF preview integration
def test_pdf_preview_integration():
    payload = {"request": get_base_payload()}
    response = client.post("/api/layouts/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-1.4")
    assert response.content.strip().endswith(b"%%EOF")
    assert b"(Amoxicillin) Tj" in response.content


# 10. Correct content types across endpoints
def test_correct_content_types():
    base = get_base_payload()
    rec_res = client.post("/api/layouts/recommend", json=base)
    assert "application/json" in rec_res.headers["content-type"]

    prev_res = client.post("/api/layouts/preview", json={"request": base})
    assert "application/json" in prev_res.headers["content-type"]

    pdf_res = client.post("/api/layouts/pdf", json={"request": base})
    assert rec_res.status_code == 200
    assert prev_res.status_code == 200
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"


# 11. Structured error responses
def test_structured_error_responses():
    # Empty body
    empty_res = client.post("/api/layouts/recommend", json={})
    assert empty_res.status_code == 422
    data = empty_res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "message" in data["error"]
    assert len(data["error"]["details"]) > 0

    # No stack trace leaked
    body_text = empty_res.text
    assert "Traceback (most recent call last)" not in body_text
    assert "File \"" not in body_text

    # PDF endpoint missing layout and request
    pdf_bad_res = client.post("/api/layouts/pdf", json={})
    assert pdf_bad_res.status_code == 422
    assert "Traceback (most recent call last)" not in pdf_bad_res.text
