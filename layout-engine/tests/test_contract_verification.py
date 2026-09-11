"""Contract verification test suite for Task 21.

Systematically verifies all 12 contract items against the actual implementation:
1. POST /api/v1/layout/optimize
2. Structured backend print-data adapter
3. QR / DataMatrix / Barcode / human-readable codes
4. dosage -> strength
5. batch_number -> batch
6. manufacturing_date -> mfg
7. expiry_date -> exp
8. serial_number -> serial_no
9. Dual scannable-code + human-readable serial placement
10. Existing legacy endpoints (/api/layouts/recommend, /preview, /pdf, /optimize)
11. SVG and PDF rendering
12. Validation and error responses
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.layout_models import (
    CodeConfig,
    CodeType,
    ElementType,
    LayoutPlan,
    LayoutRequest,
    MedicineInformation,
    PackageModel,
    StructuredPrintDataRequest,
    TabletConfig,
    parse_print_data_to_layout_request,
)
from app.optimizer.optimizer import validate_layout
from app.rendering.pdf_renderer import render_layout_to_pdf
from app.rendering.svg_renderer import render_layout_to_svg

client = TestClient(app)


# ---------------------------------------------------------------------------
# Realistic Backend Payload Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def realistic_backend_payload():
    return {
        "package": {
            "package_width_mm": 120.0,
            "package_height_mm": 60.0,
            "printing_area_width_mm": 105.0,
            "printing_area_height_mm": 50.0,
            "printing_area_x_mm": 7.5,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 6,
            "tablet_diameter_mm": 9.0,
        },
        "medicine": {
            "name": "Amoxicillin and Potassium Clavulanate",
            "dosage": "625 mg",
            "manufacturer": "HealthGuard Pharma",
        },
        "batch": {
            "batch_number": "BN-2026-9901",
            "manufacturing_date": "2026-03-01",
            "expiry_date": "2028-03-01",
        },
        "code": {
            "type": "QR",
            "value": "https://rx.zero-latency.org/v/BN20269901",
            "min_size_mm": 12.0,
            "serial_number": "SN-9901-7788",
        },
        "optimization_target": "RECOMMEND",
    }


# ---------------------------------------------------------------------------
# 1. POST /api/v1/layout/optimize Verification
# ---------------------------------------------------------------------------

def test_contract_item_1_v1_optimize_endpoint(realistic_backend_payload):
    """Verify POST /api/v1/layout/optimize accepts payload, returns 200, valid plan, strategies."""
    resp = client.post("/api/v1/layout/optimize", json=realistic_backend_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    assert data["validation"]["valid"] is True
    assert data["recommended_strategy"] in ("COST", "BALANCED", "ACCESSIBILITY")
    assert isinstance(data["score"], (int, float))
    assert len(data["elements"]) > 0
    assert len(data["alternatives"]) >= 1


# ---------------------------------------------------------------------------
# 2. Structured Backend Print-Data Adapter Verification
# ---------------------------------------------------------------------------

def test_contract_item_2_adapter_and_pydantic_model(realistic_backend_payload):
    """Verify StructuredPrintDataRequest and parse_print_data_to_layout_request adapter."""
    # Test adapter function directly
    req = parse_print_data_to_layout_request(realistic_backend_payload)
    assert isinstance(req, LayoutRequest)
    assert req.package.package_width_mm == 120.0
    assert req.tablet.tablet_count == 6

    # Test Pydantic model
    model = StructuredPrintDataRequest(**realistic_backend_payload)
    req_from_model = model.to_layout_request()
    assert isinstance(req_from_model, LayoutRequest)
    assert req_from_model.information.medicine_name == "Amoxicillin and Potassium Clavulanate"


# ---------------------------------------------------------------------------
# 3. QR / DataMatrix / Barcode / Human-Readable Code Normalization & Sizing
# ---------------------------------------------------------------------------

def test_contract_item_3_code_normalization_and_square_sizing():
    """Verify code types normalize case-insensitively and QR/DataMatrix default square."""
    # QR uppercase + square
    c_qr = CodeConfig(code_type="QR", min_size_mm=13.5)
    assert c_qr.code_type == CodeType.QR
    assert c_qr.code_width_mm == 13.5
    assert c_qr.code_height_mm == 13.5

    # DataMatrix uppercase + square
    c_dm = CodeConfig(code_type="DATAMATRIX", minimum_code_size_mm=11.0)
    assert c_dm.code_type == CodeType.DATAMATRIX
    assert c_dm.code_width_mm == 11.0
    assert c_dm.code_height_mm == 11.0

    # Barcode normalization
    c_bar = CodeConfig(code_type="BARCODE")
    assert c_bar.code_type == CodeType.BARCODE

    # Human-readable normalization
    c_hr = CodeConfig(code_type="human-readable")
    assert c_hr.code_type == CodeType.HUMAN_READABLE

    # Alias qrcode
    c_alias = CodeConfig(type="qrcode", minimum_code_size_mm=10.0)
    assert c_alias.code_type == CodeType.QR
    assert c_alias.code_width_mm == 10.0


# ---------------------------------------------------------------------------
# 4 - 8. Field Mappings (dosage, batch_number, mfg_date, exp_date, serial_number)
# ---------------------------------------------------------------------------

def test_contract_items_4_to_8_pharmaceutical_field_mappings():
    """Verify dosage->strength, batch_number->batch, mfg->mfg, exp->exp, serial->serial_no."""
    info = MedicineInformation(
        dosage="500 mg",
        batch_number="BATCH-XYZ",
        manufacturing_date="2026-02",
        expiry_date="2028-02",
        serial_number="SN-4455",
    )
    # 4. dosage -> strength
    assert info.strength == "500 mg"
    # 5. batch_number -> batch
    assert info.batch == "BATCH-XYZ"
    # 6. manufacturing_date -> mfg
    assert info.mfg == "2026-02"
    # 7. expiry_date -> exp
    assert info.exp == "2028-02"
    # 8. serial_number preserved
    assert info.serial_number == "SN-4455"

    # Verify authoritative values preserved
    authoritative = MedicineInformation(
        strength="250 mg",
        dosage="500 mg",
        batch="ORIGINAL-BATCH",
        batch_number="ALIAS-BATCH",
    )
    assert authoritative.strength == "250 mg"
    assert authoritative.batch == "ORIGINAL-BATCH"


# ---------------------------------------------------------------------------
# 9. Dual Scannable-Code + Human-Readable Serial Placement
# ---------------------------------------------------------------------------

def test_contract_item_9_dual_code_placement(realistic_backend_payload):
    """Verify concurrent placement of scannable QR code and human-readable serial text."""
    resp = client.post("/api/v1/layout/optimize", json=realistic_backend_payload)
    assert resp.status_code == 200
    elements = resp.json()["elements"]

    # Scannable code
    code_elem = next((e for e in elements if e["type"] == "code"), None)
    assert code_elem is not None
    assert code_elem["code_type"] == "qr"
    assert code_elem["content"] == "https://rx.zero-latency.org/v/BN20269901"

    # Human-readable serial text
    serial_elem = next((e for e in elements if e["id"] == "serial_no"), None)
    assert serial_elem is not None
    assert serial_elem["type"] == "text"
    assert "SN: SN-9901-7788" in serial_elem["content"]


# ---------------------------------------------------------------------------
# 10. Existing Legacy Endpoints Retained
# ---------------------------------------------------------------------------

def test_contract_item_10_legacy_endpoints_retained():
    """Verify /api/layouts/recommend, /preview, /pdf, and alias /api/layouts/optimize work."""
    req_body = {
        "package": {
            "package_width_mm": 100.0,
            "package_height_mm": 50.0,
            "printing_area_width_mm": 90.0,
            "printing_area_height_mm": 40.0,
            "printing_area_x_mm": 5.0,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {"tablet_count": 4, "tablet_diameter_mm": 8.0},
        "information": {"medicine_name": "Aspirin", "strength": "100 mg"},
    }

    # /api/layouts/recommend
    r_rec = client.post("/api/layouts/recommend", json=req_body)
    assert r_rec.status_code == 200
    assert r_rec.json()["success"] is True

    # /api/layouts/optimize (alias)
    r_opt = client.post("/api/layouts/optimize", json=req_body)
    assert r_opt.status_code == 200
    assert r_opt.json()["success"] is True

    # /api/layouts/preview
    r_prev = client.post("/api/layouts/preview", json={"request": req_body})
    assert r_prev.status_code == 200
    assert r_prev.json()["success"] is True

    # /api/layouts/pdf
    r_pdf = client.post("/api/layouts/pdf", json={"request": req_body})
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"


# ---------------------------------------------------------------------------
# 11. SVG and PDF Output Verification
# ---------------------------------------------------------------------------

def test_contract_item_11_svg_and_pdf_rendering(realistic_backend_payload):
    """Verify SVG and PDF render with QR code styling and valid document structures."""
    plan_dict = client.post("/api/v1/layout/optimize", json=realistic_backend_payload).json()
    plan = LayoutPlan(**plan_dict)

    # SVG output
    svg = render_layout_to_svg(plan)
    assert svg.startswith("<svg")
    assert "code-reserved-qr" in svg
    assert "Amoxicillin and Potassium Clavulanate" in svg

    # PDF output
    pdf = render_layout_to_pdf(plan)
    assert pdf.startswith(b"%PDF-1.4")
    assert pdf.strip().endswith(b"%%EOF")
    assert b"/MediaBox" in pdf


# ---------------------------------------------------------------------------
# 12. Validation and Error Responses Verification
# ---------------------------------------------------------------------------

def test_contract_item_12_validation_and_error_responses():
    """Verify structured HTTP 422 error response when given invalid package dimensions."""
    invalid_body = {
        "package": {
            "package_width_mm": -10.0,  # Invalid negative width
            "package_height_mm": 50.0,
            "printing_area_width_mm": 90.0,
            "printing_area_height_mm": 40.0,
        },
        "tablet": {"tablet_count": 4, "tablet_diameter_mm": 8.0},
    }
    resp = client.post("/api/v1/layout/optimize", json=invalid_body)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Comprehensive Realistic Backend Payload Verification
# ---------------------------------------------------------------------------

def test_realistic_backend_payload_comprehensive_validation(realistic_backend_payload):
    """Verify HTTP 200, valid plan, correct fields, dates, no overflow, no collision, determinism."""
    # 1. HTTP 200 and success
    resp = client.post("/api/v1/layout/optimize", json=realistic_backend_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

    # 2. Correct medicine information
    elements = data["elements"]
    name_el = next(e for e in elements if e["id"] == "med_name")
    assert name_el["content"] == "Amoxicillin and Potassium Clavulanate"
    strength_el = next(e for e in elements if e["id"] == "med_strength")
    assert strength_el["content"] == "625 mg"

    # 3. Correct batch information
    batch_el = next(e for e in elements if e["id"] == "batch_no")
    assert "BN-2026-9901" in batch_el["content"]

    # 4. Correct dates
    mfg_el = next(e for e in elements if e["id"] == "mfg_date")
    assert "2026-03-01" in mfg_el["content"]
    exp_el = next(e for e in elements if e["id"] == "exp_date")
    assert "2028-03-01" in exp_el["content"]

    # 5. QR placement
    qr_el = next(e for e in elements if e["id"] == "batch_code")
    assert qr_el["type"] == "code"
    assert qr_el["code_type"] == "qr"
    assert qr_el["width_mm"] == 12.0
    assert qr_el["height_mm"] == 12.0

    # 6. Serial placement
    sn_el = next(e for e in elements if e["id"] == "serial_no")
    assert sn_el["type"] == "text"
    assert "SN: SN-9901-7788" in sn_el["content"]

    # 7. No overflow outside boundaries
    print_x = data["package"]["printing_area_x_mm"]
    print_y = data["package"]["printing_area_y_mm"]
    print_w = data["package"]["printing_area_width_mm"]
    print_h = data["package"]["printing_area_height_mm"]
    pkg_w = data["package"]["package_width_mm"]
    pkg_h = data["package"]["package_height_mm"]

    non_cavities = [e for e in elements if e["type"] != "tablet_cavity"]
    for e in non_cavities:
        assert e["x_mm"] >= print_x - 1e-3
        assert e["y_mm"] >= print_y - 1e-3
        assert e["x_mm"] + e["width_mm"] <= print_x + print_w + 1e-3
        assert e["y_mm"] + e["height_mm"] <= print_y + print_h + 1e-3

    for e in elements:
        assert e["x_mm"] >= -1e-3
        assert e["y_mm"] >= -1e-3
        assert e["x_mm"] + e["width_mm"] <= pkg_w + 1e-3
        assert e["y_mm"] + e["height_mm"] <= pkg_h + 1e-3

    # 8. No collisions between non-cavity elements
    for i in range(len(non_cavities)):
        for j in range(i + 1, len(non_cavities)):
            e1 = non_cavities[i]
            e2 = non_cavities[j]
            no_overlap = (
                e1["x_mm"] + e1["width_mm"] <= e2["x_mm"] + 1e-3
                or e2["x_mm"] + e2["width_mm"] <= e1["x_mm"] + 1e-3
                or e1["y_mm"] + e1["height_mm"] <= e2["y_mm"] + 1e-3
                or e2["y_mm"] + e2["height_mm"] <= e1["y_mm"] + 1e-3
            )
            assert no_overlap, f"Collision detected between {e1['id']} and {e2['id']}"

    # 9. Deterministic output
    resp2 = client.post("/api/v1/layout/optimize", json=realistic_backend_payload)
    data2 = resp2.json()
    assert data["recommended_strategy"] == data2["recommended_strategy"]
    assert len(data["elements"]) == len(data2["elements"])
    for e1, e2 in zip(data["elements"], data2["elements"]):
        assert e1["id"] == e2["id"]
        assert pytest.approx(e1["x_mm"], 1e-4) == e2["x_mm"]
        assert pytest.approx(e1["y_mm"], 1e-4) == e2["y_mm"]
