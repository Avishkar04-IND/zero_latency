import copy
import pytest
from fastapi.testclient import TestClient

from app.algorithms.placement_engine import generate_layout, generate_recommendation
from app.main import app
from app.models.layout_models import (
    CodeConfig,
    CodeType,
    ElementType,
    LayoutPlan,
    LayoutRequest,
    MedicineInformation,
    PackageModel,
    PrintingConstraints,
    StructuredPrintDataRequest,
    TabletConfig,
    parse_print_data_to_layout_request,
)
from app.optimizer.optimizer import validate_layout
from app.rendering.pdf_renderer import render_layout_to_pdf
from app.rendering.svg_renderer import render_layout_to_svg

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. QR / QR uppercase / qrcode handling
# ---------------------------------------------------------------------------

def test_qr_codetype_enum():
    """Verify CodeType.QR exists and equals 'qr'."""
    assert CodeType.QR == "qr"
    assert CodeType.QR.value == "qr"


@pytest.mark.parametrize(
    "raw_input,expected",
    [
        ("qr", CodeType.QR),
        ("QR", CodeType.QR),
        ("Qr", CodeType.QR),
        ("qrcode", CodeType.QR),
        ("QRCode", CodeType.QR),
        ("QRCODE", CodeType.QR),
        ("qr-code", CodeType.QR),
        ("QR-CODE", CodeType.QR),
        ("qr_code", CodeType.QR),
    ],
)
def test_qr_normalization_variants(raw_input, expected):
    """Normalize QR code type case-insensitively and through aliases."""
    cfg = CodeConfig(code_type=raw_input, code_value="https://verify.rx/12345")
    assert cfg.code_type == expected
    assert cfg.type == expected


def test_qr_via_type_alias():
    """CodeConfig accepts 'type' alias for 'code_type'."""
    cfg = CodeConfig(type="QR", code_value="QR-SAMPLE-001")
    assert cfg.code_type == CodeType.QR
    assert cfg.type == CodeType.QR


# ---------------------------------------------------------------------------
# 2. DataMatrix / barcode case normalization
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw_input,expected",
    [
        ("datamatrix", CodeType.DATAMATRIX),
        ("DATAMATRIX", CodeType.DATAMATRIX),
        ("DataMatrix", CodeType.DATAMATRIX),
        ("data-matrix", CodeType.DATAMATRIX),
        ("DATA-MATRIX", CodeType.DATAMATRIX),
        ("barcode", CodeType.BARCODE),
        ("BARCODE", CodeType.BARCODE),
        ("BarCode", CodeType.BARCODE),
        ("bar-code", CodeType.BARCODE),
        ("BAR-CODE", CodeType.BARCODE),
        ("human-readable", CodeType.HUMAN_READABLE),
        ("HUMAN-READABLE", CodeType.HUMAN_READABLE),
        ("humanreadable", CodeType.HUMAN_READABLE),
    ],
)
def test_datamatrix_and_barcode_normalization(raw_input, expected):
    """Normalize DataMatrix, Barcode, and Human-Readable case-insensitively."""
    cfg = CodeConfig(code_type=raw_input, code_value="BATCH999")
    assert cfg.code_type == expected


# ---------------------------------------------------------------------------
# 3. Square QR / DataMatrix dimensions
# ---------------------------------------------------------------------------

def test_qr_square_dimensions_when_only_min_size_supplied():
    """QR default dimensions must be square when only minimum size is supplied."""
    cfg = CodeConfig(code_type="QR", minimum_code_size_mm=14.0)
    assert cfg.code_width_mm == 14.0
    assert cfg.code_height_mm == 14.0


def test_datamatrix_square_dimensions_when_only_min_size_supplied():
    """DataMatrix default dimensions must be square when only minimum size is supplied."""
    cfg = CodeConfig(code_type="DATAMATRIX", min_size_mm=12.5)
    assert cfg.code_width_mm == 12.5
    assert cfg.code_height_mm == 12.5


def test_explicit_dimensions_respected_over_square():
    """When explicit rectangular dimensions are supplied, they are preserved."""
    cfg = CodeConfig(code_type="DATAMATRIX", code_width_mm=18.0, code_height_mm=8.0)
    assert cfg.code_width_mm == 18.0
    assert cfg.code_height_mm == 8.0


def test_existing_behavior_preserved_when_no_min_size():
    """Preserve existing human-readable/DataMatrix/barcode behavior when min size is omitted."""
    cfg_dm = CodeConfig(code_type=CodeType.DATAMATRIX, code_value="TEST")
    assert cfg_dm.code_width_mm is None
    assert cfg_dm.code_height_mm is None

    # In placement engine, unconstrained DataMatrix defaults to 20x6 mm
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=100.0,
            package_height_mm=60.0,
            printing_area_width_mm=90.0,
            printing_area_height_mm=50.0,
            printing_area_x_mm=5.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(tablet_count=4, tablet_diameter_mm=9.0),
        code=cfg_dm,
        information=MedicineInformation(medicine_name="Aspirin"),
    )
    plan = generate_layout(req)
    assert plan.success is True
    code_elem = next(e for e in plan.elements if e.type == ElementType.CODE)
    # Either 20x6 or rotated 6x20
    dims = sorted([code_elem.width_mm, code_elem.height_mm])
    assert dims == [6.0, 20.0]


# ---------------------------------------------------------------------------
# 4. Backend pharmaceutical field mapping
# ---------------------------------------------------------------------------

def test_medicine_information_backend_field_mapping():
    """Verify backend field names map to standard layout fields."""
    info = MedicineInformation(
        medicine_name="Paracetamol",
        dosage="650 mg",
        batch_number="BATCH-2026-X",
        manufacturing_date="2026-03-01",
        expiry_date="2029-03-01",
        serial_number="SN-778899",
    )
    assert info.strength == "650 mg"
    assert info.batch == "BATCH-2026-X"
    assert info.mfg == "2026-03-01"
    assert info.exp == "2029-03-01"
    assert info.serial_number == "SN-778899"


def test_do_not_overwrite_authoritative_values():
    """Authoritative values must NOT be overwritten by backend aliases."""
    info = MedicineInformation(
        medicine_name="Paracetamol",
        strength="500 mg",  # Authoritative
        dosage="650 mg",    # Alias
        batch="B-ORIGINAL",
        batch_number="B-ALIAS",
        mfg="2026-01",
        manufacturing_date="2026-01-15",
        exp="2028-01",
        expiry_date="2028-01-31",
    )
    assert info.strength == "500 mg"
    assert info.batch == "B-ORIGINAL"
    assert info.mfg == "2026-01"
    assert info.exp == "2028-01"


# ---------------------------------------------------------------------------
# 5. Serial number placement
# ---------------------------------------------------------------------------

def test_serial_number_placement_from_info():
    """Verify serial_number in MedicineInformation generates a human-readable serial text element."""
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=110.0,
            package_height_mm=55.0,
            printing_area_width_mm=95.0,
            printing_area_height_mm=45.0,
            printing_area_x_mm=7.5,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(tablet_count=6, tablet_diameter_mm=9.0),
        information=MedicineInformation(
            medicine_name="Ciprofloxacin",
            strength="500 mg",
            serial_number="SN-CIPRO-44021",
        ),
    )
    plan = generate_layout(req)
    assert plan.success is True
    serial_elem = next((e for e in plan.elements if e.id == "serial_no"), None)
    assert serial_elem is not None
    assert serial_elem.type == ElementType.TEXT
    assert "SN-CIPRO-44021" in serial_elem.content


# ---------------------------------------------------------------------------
# 6. Dual code placement (scannable QR/DataMatrix + human-readable serial)
# ---------------------------------------------------------------------------

def test_dual_code_placement_qr_and_serial():
    """Coexistence of scannable QR code and human-readable serial text."""
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=120.0,
            package_height_mm=60.0,
            printing_area_width_mm=100.0,
            printing_area_height_mm=50.0,
            printing_area_x_mm=10.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(tablet_count=6, tablet_diameter_mm=9.0),
        code=CodeConfig(
            code_type=CodeType.QR,
            code_value="https://rx-verify.org/c/998811",
            minimum_code_size_mm=12.0,
            serial_number="SN-998811",
        ),
        information=MedicineInformation(
            medicine_name="Metformin",
            strength="850 mg",
            batch="B202604",
        ),
    )
    plan = generate_layout(req)
    assert plan.success is True

    # Check scannable code
    code_elem = next((e for e in plan.elements if e.type == ElementType.CODE), None)
    assert code_elem is not None
    assert code_elem.code_type == CodeType.QR
    assert code_elem.content == "https://rx-verify.org/c/998811"

    # Check human-readable serial text
    serial_elem = next((e for e in plan.elements if e.id == "serial_no"), None)
    assert serial_elem is not None
    assert serial_elem.type == ElementType.TEXT
    assert "SN-998811" in serial_elem.content

    # Validate that collision engine approved the layout
    val = validate_layout(plan)
    assert val.valid is True
    assert len(val.errors) == 0


def test_dual_code_placement_datamatrix_and_serial():
    """Coexistence of scannable DataMatrix and human-readable serial text."""
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=120.0,
            package_height_mm=60.0,
            printing_area_width_mm=100.0,
            printing_area_height_mm=50.0,
            printing_area_x_mm=10.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(tablet_count=6, tablet_diameter_mm=9.0),
        code=CodeConfig(
            code_type=CodeType.DATAMATRIX,
            code_value="010890123456789021SN123456",
            minimum_code_size_mm=12.0,
        ),
        information=MedicineInformation(
            medicine_name="Omeprazole",
            dosage="20 mg",
            serial_number="SN-123456",
        ),
    )
    plan = generate_layout(req)
    assert plan.success is True
    assert any(e.type == ElementType.CODE and e.code_type == CodeType.DATAMATRIX for e in plan.elements)
    assert any(e.id == "serial_no" and "SN-123456" in e.content for e in plan.elements)


# ---------------------------------------------------------------------------
# 7. Structured print data adapter
# ---------------------------------------------------------------------------

def test_structured_print_data_adapter_from_dict():
    """Convert realistic backend-style dictionary into LayoutRequest."""
    backend_payload = {
        "package": {
            "package_width_mm": 115.0,
            "package_height_mm": 55.0,
            "printing_area_width_mm": 100.0,
            "printing_area_height_mm": 45.0,
            "printing_area_x_mm": 7.5,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 6,
            "tablet_diameter_mm": 8.5,
        },
        "medicine": {
            "name": "Atorvastatin",
            "dosage": "40 mg",
            "manufacturer": "Apex Pharma",
        },
        "batch": {
            "batch_number": "ATV-2026-B1",
            "manufacturing_date": "2026-02-15",
            "expiry_date": "2029-02-15",
        },
        "code": {
            "code_type": "QR",
            "code_data": "https://verify.apex.com/rx/ATV001",
            "min_size_mm": 13.0,
            "serial_number": "ATV001-SN-8821",
        },
    }

    req = parse_print_data_to_layout_request(backend_payload)
    assert isinstance(req, LayoutRequest)
    assert req.package.package_width_mm == 115.0
    assert req.information.medicine_name == "Atorvastatin"
    assert req.information.strength == "40 mg"
    assert req.information.batch == "ATV-2026-B1"
    assert req.information.mfg == "2026-02-15"
    assert req.information.exp == "2029-02-15"
    assert req.code.code_type == CodeType.QR
    assert req.code.code_width_mm == 13.0
    assert req.code.code_height_mm == 13.0


def test_structured_print_data_adapter_codes_list():
    """Convert backend format where 'codes' is a list from /api/v1/codes/generate."""
    backend_payload = {
        "package": {
            "package_width_mm": 100.0,
            "package_height_mm": 50.0,
            "printing_area_width_mm": 90.0,
            "printing_area_height_mm": 40.0,
            "printing_area_x_mm": 5.0,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 4,
            "tablet_diameter_mm": 8.0,
        },
        "code_type": "DATAMATRIX",
        "codes": [
            {
                "serial_number": "SER-5566-01",
                "verification_url": "https://verify.rx/v/556601",
                "code_data": "01099955660121SER-5566-01",
                "min_size_mm": 11.0,
            }
        ],
        "medicine_name": "Ibuprofen",
        "dosage": "400 mg",
        "batch_number": "IBU-990",
    }

    req = parse_print_data_to_layout_request(backend_payload)
    assert req.code.code_type == CodeType.DATAMATRIX
    assert req.code.code_value == "01099955660121SER-5566-01"
    assert req.information.serial_number == "SER-5566-01"
    assert req.information.strength == "400 mg"
    assert req.information.batch == "IBU-990"


def test_structured_print_data_request_model():
    """Verify StructuredPrintDataRequest pydantic model and .to_layout_request()."""
    model = StructuredPrintDataRequest(
        package=PackageModel(
            package_width_mm=100.0,
            package_height_mm=50.0,
            printing_area_width_mm=90.0,
            printing_area_height_mm=40.0,
        ),
        tablet=TabletConfig(tablet_count=4, tablet_diameter_mm=8.0),
        dosage="200 mg",
        batch_number="B-123",
        serial_number="SN-77",
    )
    req = model.to_layout_request()
    assert req.information.strength == "200 mg"
    assert req.information.batch == "B-123"
    assert req.information.serial_number == "SN-77"


# ---------------------------------------------------------------------------
# 8. Integration route: POST /api/v1/layout/optimize
# ---------------------------------------------------------------------------

def test_v1_optimize_with_standard_request():
    """POST /api/v1/layout/optimize works with standard LayoutRequest structure."""
    payload = {
        "package": {
            "package_width_mm": 110.0,
            "package_height_mm": 55.0,
            "printing_area_width_mm": 95.0,
            "printing_area_height_mm": 45.0,
            "printing_area_x_mm": 7.5,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 6,
            "tablet_diameter_mm": 9.0,
        },
        "code": {
            "code_type": "qr",
            "code_value": "https://zero-latency.app/verify/v1/abc",
            "minimum_code_size_mm": 12.0,
        },
        "information": {
            "medicine_name": "Azithromycin",
            "strength": "500 mg",
            "batch": "AZ-881",
            "mfg": "2026-03",
            "exp": "2028-03",
        },
        "optimization_target": "RECOMMEND",
    }
    resp = client.post("/api/v1/layout/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["validation"]["valid"] is True
    assert len(data["elements"]) > 0
    assert any(e["type"] == "code" and e["code_type"] == "qr" for e in data["elements"])


def test_v1_optimize_with_structured_backend_print_data():
    """POST /api/v1/layout/optimize works with structured backend payload."""
    payload = {
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
            "manufacturer": "HealthGuard Ltd",
        },
        "batch": {
            "batch_number": "AMX-625-009",
            "manufacturing_date": "2026-04-01",
            "expiry_date": "2028-04-01",
        },
        "code": {
            "type": "QR",
            "value": "https://rx.zero-latency.org/v/AMX009",
            "min_size_mm": 13.0,
            "serial_number": "SN-AMX-009-4411",
        },
    }
    resp = client.post("/api/v1/layout/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["validation"]["valid"] is True

    elem_ids = [e["id"] for e in data["elements"]]
    assert "med_name" in elem_ids
    assert "med_strength" in elem_ids
    assert "batch_no" in elem_ids
    assert "mfg_date" in elem_ids
    assert "exp_date" in elem_ids
    assert "batch_code" in elem_ids
    assert "serial_no" in elem_ids


def test_existing_routes_remain_intact():
    """Ensure POST /api/layouts/recommend, /preview, and /pdf are unaffected."""
    payload = {
        "package": {
            "package_width_mm": 100.0,
            "package_height_mm": 50.0,
            "printing_area_width_mm": 90.0,
            "printing_area_height_mm": 40.0,
            "printing_area_x_mm": 5.0,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 4,
            "tablet_diameter_mm": 8.0,
        },
        "information": {
            "medicine_name": "Paracetamol",
            "strength": "500 mg",
        },
    }

    # /api/layouts/recommend
    r1 = client.post("/api/layouts/recommend", json=payload)
    assert r1.status_code == 200
    plan_data = r1.json()
    assert plan_data["success"] is True

    # /api/layouts/preview
    r2 = client.post("/api/layouts/preview", json={"request": payload})
    assert r2.status_code == 200
    preview_data = r2.json()
    assert preview_data["success"] is True
    assert preview_data["svg"].startswith("<svg")

    # /api/layouts/pdf
    r3 = client.post("/api/layouts/pdf", json={"request": payload})
    assert r3.status_code == 200
    assert r3.headers["content-type"] == "application/pdf"


# ---------------------------------------------------------------------------
# 9. Overflow / collision prevention
# ---------------------------------------------------------------------------

def test_overflow_and_collision_prevention():
    """Elements placed in dual-code layout never intersect or overflow margins."""
    payload = {
        "package": {
            "package_width_mm": 105.0,
            "package_height_mm": 55.0,
            "printing_area_width_mm": 95.0,
            "printing_area_height_mm": 45.0,
            "printing_area_x_mm": 5.0,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 6,
            "tablet_diameter_mm": 8.5,
        },
        "code": {
            "code_type": "QR",
            "value": "https://verify.health/sn100",
            "minimum_code_size_mm": 12.0,
            "serial_number": "SN-100200",
        },
        "information": {
            "medicine_name": "Levothyroxine",
            "dosage": "50 mcg",
            "batch_number": "LV-2026-01",
            "manufacturing_date": "2026-01",
            "expiry_date": "2028-01",
        },
    }
    resp = client.post("/api/v1/layout/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

    elements = data["elements"]
    # Check pairwise collision between non-cavity elements
    non_cavities = [e for e in elements if e["type"] != "tablet_cavity"]
    for i in range(len(non_cavities)):
        for j in range(i + 1, len(non_cavities)):
            e1 = non_cavities[i]
            e2 = non_cavities[j]
            # Verify no bounding box overlap
            no_overlap = (
                e1["x_mm"] + e1["width_mm"] <= e2["x_mm"] + 1e-3
                or e2["x_mm"] + e2["width_mm"] <= e1["x_mm"] + 1e-3
                or e1["y_mm"] + e1["height_mm"] <= e2["y_mm"] + 1e-3
                or e2["y_mm"] + e2["height_mm"] <= e1["y_mm"] + 1e-3
            )
            assert no_overlap, f"Overlap between {e1['id']} and {e2['id']}"

    # Check boundaries
    print_x = data["package"]["printing_area_x_mm"]
    print_y = data["package"]["printing_area_y_mm"]
    print_w = data["package"]["printing_area_width_mm"]
    print_h = data["package"]["printing_area_height_mm"]
    for elem in non_cavities:
        assert elem["x_mm"] >= print_x - 1e-3
        assert elem["y_mm"] >= print_y - 1e-3
        assert elem["x_mm"] + elem["width_mm"] <= print_x + print_w + 1e-3
        assert elem["y_mm"] + elem["height_mm"] <= print_y + print_h + 1e-3

    pkg_w = data["package"]["package_width_mm"]
    pkg_h = data["package"]["package_height_mm"]
    for elem in elements:
        assert elem["x_mm"] >= -1e-3
        assert elem["y_mm"] >= -1e-3
        assert elem["x_mm"] + elem["width_mm"] <= pkg_w + 1e-3
        assert elem["y_mm"] + elem["height_mm"] <= pkg_h + 1e-3


# ---------------------------------------------------------------------------
# 10. Deterministic output
# ---------------------------------------------------------------------------

def test_deterministic_output_across_repeated_runs():
    """Identical structured inputs must produce bit-for-bit identical layout elements."""
    payload = {
        "package": {
            "package_width_mm": 115.0,
            "package_height_mm": 55.0,
            "printing_area_width_mm": 100.0,
            "printing_area_height_mm": 45.0,
            "printing_area_x_mm": 7.5,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 6,
            "tablet_diameter_mm": 9.0,
        },
        "medicine": {
            "name": "Metoprolol",
            "dosage": "50 mg",
        },
        "batch": {
            "batch_number": "MET-7721",
            "expiry_date": "2027-11",
        },
        "code": {
            "type": "qr",
            "value": "https://rx.org/met/7721",
            "min_size_mm": 12.0,
            "serial_number": "SN-MET-7721-01",
        },
    }

    r1 = client.post("/api/v1/layout/optimize", json=payload).json()
    r2 = client.post("/api/v1/layout/optimize", json=payload).json()

    assert r1["success"] is True
    assert r2["success"] is True
    assert r1["recommended_strategy"] == r2["recommended_strategy"]
    assert len(r1["elements"]) == len(r2["elements"])

    for e1, e2 in zip(r1["elements"], r2["elements"]):
        assert e1["id"] == e2["id"]
        assert pytest.approx(e1["x_mm"], 1e-4) == e2["x_mm"]
        assert pytest.approx(e1["y_mm"], 1e-4) == e2["y_mm"]
        assert pytest.approx(e1["width_mm"], 1e-4) == e2["width_mm"]
        assert pytest.approx(e1["height_mm"], 1e-4) == e2["height_mm"]
        assert e1["rotation_deg"] == e2["rotation_deg"]
