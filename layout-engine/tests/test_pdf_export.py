import re
from typing import Optional
import pytest
from fastapi.testclient import TestClient

from app.algorithms.placement_engine import generate_layout
from app.main import app
from app.models.layout_models import (
    CodeConfig,
    CodeType,
    ElementType,
    LayoutElement,
    LayoutPlan,
    LayoutRequest,
    MedicineInformation,
    PackageModel,
    PrintingConstraints,
    TabletConfig,
    ValidationResult,
)
from app.rendering.pdf_renderer import MM_TO_POINTS, render_layout_to_pdf

client = TestClient(app)


def create_sample_preview_package(
    pkg_w: float = 120.0,
    pkg_h: float = 60.0,
    print_w: Optional[float] = None,
    print_h: Optional[float] = None,
    margin_x: float = 10.0,
    margin_y: float = 5.0,
) -> PackageModel:
    pw = print_w if print_w is not None else (pkg_w - 2 * margin_x)
    ph = print_h if print_h is not None else (pkg_h - 2 * margin_y)
    return PackageModel(
        package_width_mm=pkg_w,
        package_height_mm=pkg_h,
        printing_area_width_mm=pw,
        printing_area_height_mm=ph,
        printing_area_x_mm=margin_x,
        printing_area_y_mm=margin_y,
    )


# 1. Basic PDF generation
def test_basic_pdf_generation():
    pkg = create_sample_preview_package()
    plan = LayoutPlan(id="layout_pdf_001", package=pkg, elements=[])
    pdf_bytes = render_layout_to_pdf(plan)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"xref" in pdf_bytes
    assert b"trailer" in pdf_bytes
    assert pdf_bytes.strip().endswith(b"%%EOF")


# 2. Correct physical page width
def test_correct_physical_page_width():
    pkg_w_mm = 140.0
    pkg_h_mm = 70.0
    expected_w_pt = pkg_w_mm * MM_TO_POINTS
    pkg = create_sample_preview_package(pkg_w=pkg_w_mm, pkg_h=pkg_h_mm)
    plan = LayoutPlan(package=pkg, elements=[])
    pdf_bytes = render_layout_to_pdf(plan)

    # Check MediaBox in PDF
    mediabox_match = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d\.]+)\s+([\d\.]+)\s*\]", pdf_bytes)
    assert mediabox_match is not None
    w_pt = float(mediabox_match.group(1))
    assert w_pt == pytest.approx(expected_w_pt, rel=1e-3)


# 3. Correct physical page height
def test_correct_physical_page_height():
    pkg_w_mm = 120.0
    pkg_h_mm = 80.0
    expected_h_pt = pkg_h_mm * MM_TO_POINTS
    pkg = create_sample_preview_package(pkg_w=pkg_w_mm, pkg_h=pkg_h_mm)
    plan = LayoutPlan(package=pkg, elements=[])
    pdf_bytes = render_layout_to_pdf(plan)

    mediabox_match = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d\.]+)\s+([\d\.]+)\s*\]", pdf_bytes)
    assert mediabox_match is not None
    h_pt = float(mediabox_match.group(2))
    assert h_pt == pytest.approx(expected_h_pt, rel=1e-3)


# 4. Package boundary
def test_package_boundary():
    pkg_w_mm = 100.0
    pkg_h_mm = 50.0
    pkg = create_sample_preview_package(pkg_w=pkg_w_mm, pkg_h=pkg_h_mm)
    plan = LayoutPlan(package=pkg, elements=[])
    pdf_bytes = render_layout_to_pdf(plan)

    w_pt = pkg_w_mm * MM_TO_POINTS
    h_pt = pkg_h_mm * MM_TO_POINTS
    expected_re = f"0 0 {w_pt:.3f} {h_pt:.3f} re B".encode("ascii")
    assert expected_re in pdf_bytes
    assert b"% --- Package Boundary ---" in pdf_bytes


# 5. Printable area
def test_printable_area():
    pkg = create_sample_preview_package(
        pkg_w=120.0,
        pkg_h=60.0,
        print_w=100.0,
        print_h=50.0,
        margin_x=10.0,
        margin_y=5.0,
    )
    plan = LayoutPlan(package=pkg, elements=[])
    pdf_bytes = render_layout_to_pdf(plan)

    pa_x_pt = 10.0 * MM_TO_POINTS
    pa_y_pt = (60.0 - (5.0 + 50.0)) * MM_TO_POINTS
    pa_w_pt = 100.0 * MM_TO_POINTS
    pa_h_pt = 50.0 * MM_TO_POINTS

    expected_re = f"{pa_x_pt:.3f} {pa_y_pt:.3f} {pa_w_pt:.3f} {pa_h_pt:.3f} re B".encode("ascii")
    assert expected_re in pdf_bytes
    assert b"% --- Printable Area ---" in pdf_bytes
    assert b"[2 2] 0 d" in pdf_bytes  # Dashed stroke for printable area


# 6. Tablet cavities (round and non-round)
def test_tablet_cavities():
    pkg = create_sample_preview_package()
    elements = [
        # Round tablet cavity (w == h)
        LayoutElement(
            id="cavity_round",
            type=ElementType.TABLET_CAVITY,
            x_mm=20.0,
            y_mm=15.0,
            width_mm=10.0,
            height_mm=10.0,
        ),
        # Non-round capsule cavity (w != h)
        LayoutElement(
            id="cavity_capsule",
            type=ElementType.TABLET_CAVITY,
            x_mm=40.0,
            y_mm=15.0,
            width_mm=18.0,
            height_mm=8.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    pdf_bytes = render_layout_to_pdf(plan)

    assert b"% --- Element: cavity_round (tablet_cavity) ---" in pdf_bytes
    assert b"% --- Element: cavity_capsule (tablet_cavity) ---" in pdf_bytes

    # Round cavity should contain cubic Bézier curves 'c'
    assert b" c " in pdf_bytes or b" c\n" in pdf_bytes

    # Capsule/oblong cavity should contain rectangle 're'
    capsule_w_pt = 18.0 * MM_TO_POINTS
    capsule_h_pt = 8.0 * MM_TO_POINTS
    assert f"{capsule_w_pt:.3f} {capsule_h_pt:.3f} re B".encode("ascii") in pdf_bytes


# 7. Text elements
def test_text_rendering():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="med_name",
            type=ElementType.TEXT,
            content="Amoxicillin Trihydrate",
            x_mm=15.0,
            y_mm=10.0,
            width_mm=50.0,
            height_mm=5.0,
            font_size_mm=3.0,
        ),
        LayoutElement(
            id="strength",
            type=ElementType.TEXT,
            content="500 mg",
            x_mm=15.0,
            y_mm=16.0,
            width_mm=20.0,
            height_mm=4.0,
            font_size_mm=2.5,
        ),
        LayoutElement(
            id="batch_info",
            type=ElementType.TEXT,
            content="B.No: BX-9921",
            x_mm=15.0,
            y_mm=22.0,
            width_mm=30.0,
            height_mm=3.5,
            font_size_mm=2.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    pdf_bytes = render_layout_to_pdf(plan)

    assert b"(Amoxicillin Trihydrate) Tj" in pdf_bytes
    assert b"(500 mg) Tj" in pdf_bytes
    assert b"(B.No: BX-9921) Tj" in pdf_bytes
    # Check font selection
    assert b"/F2" in pdf_bytes  # Helvetica-Bold for medicine name
    assert b"/F1" in pdf_bytes  # Helvetica for standard text


# 8. Human-readable MED001 code
def test_human_readable_med001_code():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="code_1",
            type=ElementType.CODE,
            content="MED001",
            x_mm=15.0,
            y_mm=40.0,
            width_mm=25.0,
            height_mm=6.0,
            code_type=CodeType.HUMAN_READABLE,
        )
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    pdf_bytes = render_layout_to_pdf(plan)

    assert b"(MED001) Tj" in pdf_bytes
    assert b"/F3" in pdf_bytes  # Courier monospace font for human-readable code


# 9. DataMatrix reserved area
def test_datamatrix_reserved_area():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="code_dm",
            type=ElementType.CODE,
            content="MED001-DM",
            x_mm=80.0,
            y_mm=15.0,
            width_mm=14.0,
            height_mm=14.0,
            code_type=CodeType.DATAMATRIX,
        )
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    pdf_bytes = render_layout_to_pdf(plan)

    assert b"[2 1] 0 d" in pdf_bytes  # Dashed pattern for DataMatrix reserved zone
    assert b"([DataMatrix: MED001-DM]) Tj" in pdf_bytes
    # Ensure no actual 2D barcode symbols or embedded images are present
    assert b"/Subtype /Image" not in pdf_bytes
    assert b"/XObject" not in pdf_bytes


# 10. Barcode reserved area
def test_barcode_reserved_area():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="code_bc",
            type=ElementType.CODE,
            content="8901234567890",
            x_mm=60.0,
            y_mm=40.0,
            width_mm=35.0,
            height_mm=12.0,
            code_type=CodeType.BARCODE,
        )
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    pdf_bytes = render_layout_to_pdf(plan)

    assert b"[3 1.5] 0 d" in pdf_bytes  # Dashed pattern for Barcode reserved zone
    assert b"([Barcode: 8901234567890]) Tj" in pdf_bytes
    assert b"/Subtype /Image" not in pdf_bytes
    assert b"/XObject" not in pdf_bytes


# 11. Rotation transform
def test_rotation_transform():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="rotated_text",
            type=ElementType.TEXT,
            content="SIDE LABEL",
            x_mm=105.0,
            y_mm=15.0,
            width_mm=8.0,
            height_mm=30.0,
            rotation_deg=90.0,
        )
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    pdf_bytes = render_layout_to_pdf(plan)

    # Coordinate transformation matrix 'cm'
    assert b" cm\n" in pdf_bytes or b" cm " in pdf_bytes
    assert b"(SIDE LABEL) Tj" in pdf_bytes


# 12. PDF generated from actual optimized LayoutPlan
def test_pdf_generated_from_actual_optimized_layout_plan():
    req = LayoutRequest(
        package=create_sample_preview_package(pkg_w=140.0, pkg_h=70.0, print_w=120.0, print_h=60.0),
        tablet=TabletConfig(tablet_count=10, tablet_diameter_mm=8.0),
        information=MedicineInformation(
            medicine_name="Paracetamol",
            strength="650 mg",
            batch_number="B123",
            expiry_date="12/28",
        ),
        code=CodeConfig(type=CodeType.DATAMATRIX, code_value="MED-BATCH-001"),
        constraints=PrintingConstraints(minimum_margin_mm=2.0, minimum_element_spacing_mm=1.0),
    )
    plan = generate_layout(req)
    assert plan.success is True
    assert len(plan.elements) > 0

    pdf_bytes = render_layout_to_pdf(plan)
    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"(Paracetamol) Tj" in pdf_bytes
    assert b"(650 mg) Tj" in pdf_bytes
    assert b"([DataMatrix: MED-BATCH-001]) Tj" in pdf_bytes


# 13. Invalid layout handling
def test_invalid_layout_handling():
    # Null plan
    with pytest.raises(ValueError, match="LayoutPlan is None"):
        render_layout_to_pdf(None)

    # Missing package
    invalid_plan = LayoutPlan(package=None, elements=[])
    with pytest.raises(ValueError, match="missing package information"):
        render_layout_to_pdf(invalid_plan)

    # Failed layout (success=False)
    failed_plan = LayoutPlan(
        package=create_sample_preview_package(),
        elements=[],
        success=False,
        errors=["Element overlap detected", "Exceeds boundary"],
        validation=ValidationResult(valid=False, errors=["Element overlap detected", "Exceeds boundary"]),
    )
    with pytest.raises(ValueError, match="Cannot render PDF"):
        render_layout_to_pdf(failed_plan)

    # Invalid validation (validation.valid=False)
    invalid_val_plan = LayoutPlan(
        package=create_sample_preview_package(),
        elements=[],
        validation=ValidationResult(valid=False, errors=["Placement validation failed"]),
    )
    with pytest.raises(ValueError, match="Cannot render PDF"):
        render_layout_to_pdf(invalid_val_plan)

    # Zero package dimension
    zero_plan = LayoutPlan(package=create_sample_preview_package(), elements=[])
    object.__setattr__(zero_plan.package, "package_width_mm", 0.0)
    with pytest.raises(ValueError, match="Invalid package dimensions"):
        render_layout_to_pdf(zero_plan)


# 14. PDF API endpoint tests
def test_pdf_api_endpoint():
    # Successful PDF export with request parameter
    payload = {
        "request": {
            "package": {
                "package_width_mm": 130.0,
                "package_height_mm": 65.0,
                "printing_area_width_mm": 110.0,
                "printing_area_height_mm": 55.0,
                "printing_area_x_mm": 10.0,
                "printing_area_y_mm": 5.0,
            },
            "tablet": {"tablet_count": 6, "tablet_diameter_mm": 9.0},
            "information": {
                "medicine_name": "Ibuprofen",
                "strength": "400 mg",
            },
            "code": {"type": "datamatrix", "code_value": "IBU400"},
            "constraints": {"minimum_margin_mm": 2.0, "minimum_element_spacing_mm": 1.0},
        }
    }
    response = client.post("/api/layouts/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-1.4")
    assert b"(Ibuprofen) Tj" in response.content

    # Failure when layout generation fails (e.g. 500 tablets in tiny package)
    impossible_payload = {
        "request": {
            "package": {
                "package_width_mm": 20.0,
                "package_height_mm": 15.0,
                "printing_area_width_mm": 10.0,
                "printing_area_height_mm": 8.0,
                "printing_area_x_mm": 5.0,
                "printing_area_y_mm": 3.0,
            },
            "tablet": {"tablet_count": 100, "tablet_diameter_mm": 10.0},
            "constraints": {"minimum_margin_mm": 2.0, "minimum_element_spacing_mm": 1.0},
        }
    }
    fail_response = client.post("/api/layouts/pdf", json=impossible_payload)
    assert fail_response.status_code == 400
    fail_json = fail_response.json()
    assert "Layout generation failed" in str(fail_json)


# 15. Determinism and aspect ratio preservation
def test_determinism_and_aspect_ratio():
    pkg_w = 150.0
    pkg_h = 75.0
    pkg = create_sample_preview_package(pkg_w=pkg_w, pkg_h=pkg_h)
    plan = LayoutPlan(
        id="det_plan",
        package=pkg,
        elements=[
            LayoutElement(
                id="t1",
                type=ElementType.TEXT,
                content="Deterministic Text",
                x_mm=20.0,
                y_mm=20.0,
                width_mm=30.0,
                height_mm=5.0,
            )
        ],
    )

    pdf1 = render_layout_to_pdf(plan)
    pdf2 = render_layout_to_pdf(plan)

    # Determinism: exact byte equality
    assert pdf1 == pdf2

    # Aspect ratio check
    mediabox_match = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d\.]+)\s+([\d\.]+)\s*\]", pdf1)
    assert mediabox_match is not None
    w_pt = float(mediabox_match.group(1))
    h_pt = float(mediabox_match.group(2))
    assert (w_pt / h_pt) == pytest.approx(pkg_w / pkg_h, rel=1e-4)
