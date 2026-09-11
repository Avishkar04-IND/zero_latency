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
from app.rendering.svg_renderer import render_layout_to_svg

client = TestClient(app)


def create_sample_preview_package(
    pkg_w: float = 120.0,
    pkg_h: float = 60.0,
    print_w: float = 100.0,
    print_h: float = 50.0,
    margin_x: float = 10.0,
    margin_y: float = 5.0,
) -> PackageModel:
    return PackageModel(
        package_width_mm=pkg_w,
        package_height_mm=pkg_h,
        printing_area_width_mm=print_w,
        printing_area_height_mm=print_h,
        printing_area_x_mm=margin_x,
        printing_area_y_mm=margin_y,
    )


# 1. Basic SVG generation
def test_basic_svg_generation():
    pkg = create_sample_preview_package()
    plan = LayoutPlan(id="layout_test_001", package=pkg, elements=[])
    svg = render_layout_to_svg(plan)
    assert svg.startswith("<svg")
    assert svg.strip().endswith("</svg>")
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg


# 2. Correct package dimensions
def test_correct_package_dimensions():
    pkg = create_sample_preview_package(pkg_w=150.0, pkg_h=75.0)
    plan = LayoutPlan(package=pkg, elements=[])
    svg = render_layout_to_svg(plan)
    assert 'width="150.0mm"' in svg
    assert 'height="75.0mm"' in svg
    assert 'viewBox="0 0 150.0 75.0"' in svg
    assert '<rect class="package-boundary" x="0" y="0" width="150.0" height="75.0"' in svg


# 3. Correct printable area
def test_correct_printable_area():
    pkg = create_sample_preview_package(pkg_w=120.0, pkg_h=60.0, print_w=100.0, print_h=50.0, margin_x=10.0, margin_y=5.0)
    plan = LayoutPlan(package=pkg, elements=[])
    svg = render_layout_to_svg(plan)
    assert '<rect class="print-area" x="10.0" y="5.0" width="100.0" height="50.0"' in svg


# 4. Multiple tablet cavities
def test_multiple_tablet_cavities():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(id="cavity_1", type=ElementType.TABLET_CAVITY, x_mm=15.0, y_mm=10.0, width_mm=8.0, height_mm=8.0),
        LayoutElement(id="cavity_2", type=ElementType.TABLET_CAVITY, x_mm=25.0, y_mm=10.0, width_mm=8.0, height_mm=8.0),
        LayoutElement(id="cavity_3", type=ElementType.TABLET_CAVITY, x_mm=35.0, y_mm=10.0, width_mm=8.0, height_mm=8.0),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    assert 'id="cavity_1"' in svg
    assert 'id="cavity_2"' in svg
    assert 'id="cavity_3"' in svg
    assert svg.count('class="tablet-cavity"') == 3


# 5. Round tablet rendering
def test_round_tablet_rendering():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(id="round_cavity", type=ElementType.TABLET_CAVITY, x_mm=20.0, y_mm=15.0, width_mm=10.0, height_mm=10.0),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    # Circle tag with center at cx=25.0, cy=20.0 and radius r=5.0
    assert '<circle class="tablet-cavity"' in svg
    assert 'data-shape="round"' in svg
    assert 'cx="25.0"' in svg
    assert 'cy="20.0"' in svg
    assert 'r="5.0"' in svg


# 6. Non-round tablet rendering
def test_non_round_tablet_rendering():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(id="oblong_cavity", type=ElementType.TABLET_CAVITY, x_mm=20.0, y_mm=15.0, width_mm=16.0, height_mm=8.0),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    # Rect tag with bounding geometry
    assert '<rect class="tablet-cavity"' in svg
    assert 'data-shape="non-round"' in svg
    assert 'x="20.0"' in svg
    assert 'y="15.0"' in svg
    assert 'width="16.0"' in svg
    assert 'height="8.0"' in svg


# 7. Text rendering
def test_text_rendering():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(id="med_name", type=ElementType.TEXT, content="Amoxicillin", x_mm=10.0, y_mm=10.0, width_mm=30.0, height_mm=5.0, font_size_mm=3.5),
        LayoutElement(id="med_strength", type=ElementType.TEXT, content="500 mg", x_mm=10.0, y_mm=16.0, width_mm=20.0, height_mm=4.0, font_size_mm=2.8),
        LayoutElement(id="warnings", type=ElementType.TEXT, content="Keep & Store Dry <25C>", x_mm=10.0, y_mm=22.0, width_mm=40.0, height_mm=4.0, font_size_mm=2.0),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    assert 'id="med_name"' in svg
    assert 'Amoxicillin' in svg
    assert 'font-size="3.5mm"' in svg
    assert 'id="med_strength"' in svg
    assert '500 mg' in svg
    assert 'font-size="2.8mm"' in svg
    # XML escaping
    assert "Keep &amp; Store Dry &lt;25C&gt;" in svg


# 8. Human-readable MED001 rendering
def test_human_readable_med001_rendering():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="batch_code",
            type=ElementType.CODE,
            content="MED001",
            code_type=CodeType.HUMAN_READABLE,
            x_mm=30.0,
            y_mm=15.0,
            width_mm=20.0,
            height_mm=6.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    assert 'class="layout-code-group code-human-readable"' in svg
    assert "MED001" in svg


# 9. DataMatrix reserved-area rendering
def test_datamatrix_reserved_area_rendering():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="dm_code",
            type=ElementType.CODE,
            content="MED001",
            code_type=CodeType.DATAMATRIX,
            x_mm=40.0,
            y_mm=20.0,
            width_mm=15.0,
            height_mm=15.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    assert "code-datamatrix" in svg
    assert "code-reserved-datamatrix" in svg
    assert "[DataMatrix: MED001]" in svg


# 10. Barcode reserved-area rendering
def test_barcode_reserved_area_rendering():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(
            id="bc_code",
            type=ElementType.CODE,
            content="MED001",
            code_type=CodeType.BARCODE,
            x_mm=30.0,
            y_mm=25.0,
            width_mm=25.0,
            height_mm=8.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    assert "code-barcode" in svg
    assert "code-reserved-barcode" in svg
    assert "[Barcode: MED001]" in svg


# 11. Element rotation
def test_element_rotation():
    pkg = create_sample_preview_package()
    elements = [
        LayoutElement(id="rot_text", type=ElementType.TEXT, content="Side Info", x_mm=50.0, y_mm=20.0, width_mm=20.0, height_mm=5.0, rotation_deg=90.0),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)
    # Center is cx = 50 + 10 = 60.0, cy = 20 + 2.5 = 22.5
    assert 'transform="rotate(90.0 60.0 22.5)"' in svg


# 12. SVG generated from actual optimized layout
def test_svg_generated_from_actual_optimized_layout():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=120.0,
            package_height_mm=60.0,
            printing_area_width_mm=100.0,
            printing_area_height_mm=50.0,
            printing_area_x_mm=5.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(
            tablet_count=6,
            tablet_diameter_mm=8.0,
        ),
        code=CodeConfig(
            code_value="MED001",
            code_width_mm=20.0,
            code_height_mm=6.0,
        ),
        information=MedicineInformation(
            medicine_name="Paracetamol",
            strength="500 mg",
            batch="B2026",
            mfg="2026-01",
            exp="2028-01",
            warnings="Keep dry",
        ),
        constraints=PrintingConstraints(
            minimum_margin_mm=1.5,
            minimum_element_spacing_mm=1.2,
        ),
        optimization_target="RECOMMEND",
    )
    plan = generate_layout(req)
    assert plan.success is True

    svg = render_layout_to_svg(plan)
    assert svg.startswith("<svg")
    assert "Paracetamol" in svg
    assert "500 mg" in svg
    assert "MED001" in svg
    assert "cavity_1" in svg
    assert "cavity_6" in svg


# 13. Preview API
def test_preview_api():
    payload = {
        "request": {
            "package": {
                "package_width_mm": 110.0,
                "package_height_mm": 55.0,
                "printing_area_width_mm": 90.0,
                "printing_area_height_mm": 45.0,
                "margin_left_mm": 5.0,
                "margin_top_mm": 5.0,
            },
            "tablet": {
                "tablet_count": 4,
                "tablet_diameter_mm": 8.0,
            },
            "code": {
                "code_value=":"MED001",
                "value": "MED001",
            },
            "information": {
                "medicine_name": "Ibuprofen",
                "strength": "400 mg",
            },
            "optimization_target": "RECOMMEND",
        }
    }
    response = client.post("/api/layouts/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "svg" in data
    assert data["svg"].startswith("<svg")
    assert "Ibuprofen" in data["svg"]
    assert "validation" in data
    assert data["validation"]["valid"] is True


# 14. Invalid layout handling
def test_invalid_layout_handling():
    pkg = create_sample_preview_package()
    failed_plan = LayoutPlan(
        id="layout_failed",
        package=pkg,
        elements=[],
        success=False,
        errors=["Insufficient printable area"],
        validation=ValidationResult(valid=False, errors=["Insufficient printable area"]),
    )
    # Direct renderer call raises ValueError on unsuccessful plan
    with pytest.raises(ValueError) as excinfo:
        render_layout_to_svg(failed_plan)
    assert "Insufficient printable area" in str(excinfo.value)

    # API handles failed layout cleanly without generating fake SVG
    payload = {
        "layout": failed_plan.model_dump(),
    }
    response = client.post("/api/layouts/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["svg"] is None
    assert "errors" in data
    assert len(data["errors"]) > 0


# 15. Valid SVG structure
def test_valid_svg_structure():
    pkg = create_sample_preview_package()
    plan = LayoutPlan(package=pkg, elements=[])
    svg = render_layout_to_svg(plan)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "<style>" in svg
    assert "</style>" in svg
    assert "<rect" in svg
