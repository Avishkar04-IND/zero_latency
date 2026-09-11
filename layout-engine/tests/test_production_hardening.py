import time
import pytest
from fastapi.testclient import TestClient

from app.algorithms.placement_engine import (
    generate_accessibility_layout,
    generate_balanced_layout,
    generate_cost_optimized_layout,
    generate_layout,
    generate_recommendation,
)
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
    TabletCavityPosition,
    TabletConfig,
)
from app.optimizer.optimizer import validate_layout
from app.rendering.pdf_renderer import render_layout_to_pdf
from app.rendering.svg_renderer import render_layout_to_svg

client = TestClient(app)


def make_standard_request(
    pkg_w: float = 120.0,
    pkg_h: float = 60.0,
    print_w: float = 100.0,
    print_h: float = 50.0,
    margin_x: float = 10.0,
    margin_y: float = 5.0,
    count: int = 6,
    diam: float = 9.0,
    opt_target: str = "RECOMMEND",
) -> LayoutRequest:
    return LayoutRequest(
        package=PackageModel(
            package_width_mm=pkg_w,
            package_height_mm=pkg_h,
            printing_area_width_mm=print_w,
            printing_area_height_mm=print_h,
            printing_area_x_mm=margin_x,
            printing_area_y_mm=margin_y,
        ),
        tablet=TabletConfig(tablet_count=count, tablet_diameter_mm=diam),
        code=CodeConfig(code_type=CodeType.DATAMATRIX, code_value="MED-BATCH-001"),
        information=MedicineInformation(
            medicine_name="Amoxicillin",
            strength="500 mg",
            batch="B102",
            mfg="2026-01",
            exp="2028-01",
        ),
        constraints=PrintingConstraints(minimum_margin_mm=1.5, minimum_element_spacing_mm=1.0),
        optimization_target=opt_target,
    )


# 1. Very small package
def test_edge_case_very_small_package():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=55.0,
            package_height_mm=35.0,
            printing_area_width_mm=47.0,
            printing_area_height_mm=27.0,
            printing_area_x_mm=4.0,
            printing_area_y_mm=4.0,
        ),
        tablet=TabletConfig(tablet_count=1, tablet_diameter_mm=7.0),
        code=CodeConfig(code_type=CodeType.DATAMATRIX, code_value="M1", min_size_mm=8.0),
        information=MedicineInformation(medicine_name="Aspirin", strength="75 mg"),
        constraints=PrintingConstraints(minimum_margin_mm=1.0, minimum_element_spacing_mm=0.8),
        optimization_target="COST",
    )
    plan = generate_layout(req)
    assert plan.success is True
    assert len(plan.elements) >= 3
    assert plan.validation.valid is True


# 2. Very large package
def test_edge_case_very_large_package():
    req = make_standard_request(
        pkg_w=300.0,
        pkg_h=150.0,
        print_w=270.0,
        print_h=130.0,
        margin_x=15.0,
        margin_y=10.0,
        count=12,
        diam=10.0,
    )
    plan = generate_layout(req)
    assert plan.success is True
    assert plan.package.package_width_mm == 300.0
    assert plan.validation.valid is True


# 3. One tablet
def test_edge_case_one_tablet():
    req = make_standard_request(count=1, diam=10.0)
    plan = generate_layout(req)
    assert plan.success is True
    cavities = [e for e in plan.elements if e.type == ElementType.TABLET_CAVITY]
    assert len(cavities) == 1


# 4. Multiple tablets
def test_edge_case_multiple_tablets():
    req = make_standard_request(count=10, diam=8.0)
    plan = generate_layout(req)
    assert plan.success is True
    cavities = [e for e in plan.elements if e.type == ElementType.TABLET_CAVITY]
    assert len(cavities) == 10


# 5. High tablet count
def test_edge_case_high_tablet_count():
    req = make_standard_request(
        pkg_w=180.0,
        pkg_h=90.0,
        print_w=160.0,
        print_h=75.0,
        margin_x=10.0,
        margin_y=7.5,
        count=20,
        diam=8.0,
        opt_target="COST",
    )
    plan = generate_layout(req)
    assert plan.success is True
    cavities = [e for e in plan.elements if e.type == ElementType.TABLET_CAVITY]
    assert len(cavities) == 20
    assert plan.validation.valid is True


# 6. Round tablets
def test_edge_case_round_tablets():
    req = make_standard_request(count=4, diam=9.0)
    plan = generate_layout(req)
    assert plan.success is True
    cavities = [e for e in plan.elements if e.type == ElementType.TABLET_CAVITY]
    for c in cavities:
        assert abs(c.width_mm - c.height_mm) < 1e-4
    # Round cavities in SVG and PDF
    svg = render_layout_to_svg(plan)
    assert 'data-shape="round"' in svg
    pdf = render_layout_to_pdf(plan)
    assert b" c " in pdf or b" c\n" in pdf


# 7. Non-round tablets (capsule/oblong)
def test_edge_case_non_round_tablets():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=140.0,
            package_height_mm=70.0,
            printing_area_width_mm=120.0,
            printing_area_height_mm=55.0,
            printing_area_x_mm=10.0,
            printing_area_y_mm=7.5,
        ),
        tablet=TabletConfig(tablet_count=4, tablet_width_mm=16.0, tablet_height_mm=7.0),
        code=CodeConfig(code_type=CodeType.HUMAN_READABLE, code_value="MED001"),
        information=MedicineInformation(medicine_name="Cephalexin", strength="500 mg"),
    )
    plan = generate_layout(req)
    assert plan.success is True
    cavities = [e for e in plan.elements if e.type == ElementType.TABLET_CAVITY]
    assert len(cavities) == 4
    for c in cavities:
        assert abs(c.width_mm - 16.0) < 1e-4
        assert abs(c.height_mm - 7.0) < 1e-4
    svg = render_layout_to_svg(plan)
    assert 'data-shape="non-round"' in svg


# 8. Very small code
def test_edge_case_very_small_code():
    req = make_standard_request()
    req.code = CodeConfig(
        code_type=CodeType.DATAMATRIX,
        code_value="M1",
        code_width_mm=6.0,
        code_height_mm=6.0,
    )
    plan = generate_layout(req)
    assert plan.success is True
    code_elem = next(e for e in plan.elements if e.type == ElementType.CODE)
    assert code_elem.width_mm <= 6.0 or code_elem.height_mm <= 6.0


# 9. Large code
def test_edge_case_large_code():
    req = make_standard_request(pkg_w=150.0, pkg_h=80.0, print_w=130.0, print_h=65.0)
    req.code = CodeConfig(
        code_type=CodeType.BARCODE,
        code_value="8901234567890",
        code_width_mm=32.0,
        code_height_mm=12.0,
    )
    plan = generate_layout(req)
    assert plan.success is True
    code_elem = next(e for e in plan.elements if e.type == ElementType.CODE)
    assert code_elem.width_mm >= 12.0


# 10. Code requiring rotation
def test_edge_case_code_requiring_rotation():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=100.0,
            package_height_mm=50.0,
            printing_area_width_mm=80.0,
            printing_area_height_mm=40.0,
            printing_area_x_mm=10.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(tablet_count=2, tablet_diameter_mm=8.0),
        code=CodeConfig(
            code_type=CodeType.BARCODE,
            code_value="1234567890128",
            code_width_mm=25.0,
            code_height_mm=8.0,
            orientation_deg=90.0,
        ),
        information=MedicineInformation(medicine_name="Aspirin"),
    )
    plan = generate_layout(req)
    assert plan.success is True
    code_elem = next(e for e in plan.elements if e.type == ElementType.CODE)
    assert code_elem.rotation_deg in (0.0, 90.0, 180.0, 270.0)


# 11. Very small printable area
def test_edge_case_very_small_printable_area():
    # Compact printable area with single tablet and minimal medicine name
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=50.0,
            package_height_mm=32.0,
            printing_area_width_mm=40.0,
            printing_area_height_mm=22.0,
            printing_area_x_mm=5.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(tablet_count=1, tablet_diameter_mm=7.0),
        code=CodeConfig(code_type=CodeType.DATAMATRIX, code_value="MED1", min_size_mm=7.0),
        information=MedicineInformation(medicine_name="Aspirin"),
        constraints=PrintingConstraints(minimum_margin_mm=1.0, minimum_element_spacing_mm=0.8),
        optimization_target="COST",
    )
    plan = generate_layout(req)
    assert plan.success is True
    assert plan.validation.valid is True


# 12. Printable area equal to package boundary
def test_edge_case_printable_area_equal_to_package_boundary():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=80.0,
            package_height_mm=40.0,
            printing_area_width_mm=80.0,
            printing_area_height_mm=40.0,
            printing_area_x_mm=0.0,
            printing_area_y_mm=0.0,
        ),
        tablet=TabletConfig(tablet_count=2, tablet_diameter_mm=8.0),
        information=MedicineInformation(medicine_name="Paracetamol"),
    )
    plan = generate_layout(req)
    assert plan.success is True
    assert plan.package.printing_area_width_mm == plan.package.package_width_mm
    assert plan.package.printing_area_height_mm == plan.package.package_height_mm


# 13. Large margins
def test_edge_case_large_margins():
    req = make_standard_request(
        pkg_w=150.0,
        pkg_h=80.0,
        print_w=100.0,
        print_h=50.0,
        margin_x=25.0,
        margin_y=15.0,
        count=4,
        diam=8.0,
    )
    req.constraints.minimum_margin_mm = 6.0
    plan = generate_layout(req)
    assert plan.success is True
    assert plan.validation.valid is True


# 14. Zero or negative dimensions
def test_edge_case_zero_negative_dimensions():
    with pytest.raises(Exception):
        PackageModel(
            package_width_mm=-10.0,
            package_height_mm=50.0,
            printing_area_width_mm=40.0,
            printing_area_height_mm=30.0,
            printing_area_x_mm=5.0,
            printing_area_y_mm=5.0,
        )

    with pytest.raises(Exception):
        TabletConfig(tablet_count=0, tablet_diameter_mm=8.0)


# 15. Overlapping supplied tablet cavities
def test_edge_case_overlapping_supplied_tablet_cavities():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=100.0,
            package_height_mm=50.0,
            printing_area_width_mm=80.0,
            printing_area_height_mm=40.0,
            printing_area_x_mm=10.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(
            tablet_count=2,
            tablet_diameter_mm=10.0,
            positions=[
                TabletCavityPosition(x_mm=20.0, y_mm=20.0),
                TabletCavityPosition(x_mm=22.0, y_mm=20.0),  # Overlaps!
            ],
        ),
    )
    plan = generate_layout(req)
    # Collision detection must catch overlap
    assert plan.validation.valid is False or plan.success is False


# 16. Tablet cavity outside package boundary
def test_edge_case_tablet_cavity_outside_package():
    with pytest.raises(ValueError, match="exceeds package"):
        LayoutRequest(
            package=PackageModel(
                package_width_mm=80.0,
                package_height_mm=40.0,
                printing_area_width_mm=60.0,
                printing_area_height_mm=30.0,
                printing_area_x_mm=10.0,
                printing_area_y_mm=5.0,
            ),
            tablet=TabletConfig(
                tablet_count=1,
                tablet_diameter_mm=10.0,
                positions=[TabletCavityPosition(x_mm=75.0, y_mm=20.0)],  # 75 + 10 = 85 > 80!
            ),
        )


# 17. Text and code collision prevention
def test_edge_case_text_code_collision_prevented():
    from app.geometry.geometry import Rect

    req = make_standard_request(count=4, diam=8.0)
    plan = generate_layout(req)
    assert plan.success is True

    # Validate that none of the elements collide with each other
    validation = validate_layout(plan)
    assert validation.valid is True
    assert len(validation.errors) == 0

    # Explicit pairwise bounding box collision check
    rects = [Rect(e.x_mm, e.y_mm, e.width_mm, e.height_mm) for e in plan.elements]
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            assert rects[i].intersects(rects[j]) is False


# 18. Insufficient spacing validation
def test_edge_case_insufficient_spacing_validation():
    pkg = PackageModel(
        package_width_mm=100.0,
        package_height_mm=50.0,
        printing_area_width_mm=80.0,
        printing_area_height_mm=40.0,
        printing_area_x_mm=10.0,
        printing_area_y_mm=5.0,
    )
    # Two elements placed with only 0.2mm separation when 2.0mm spacing is required
    plan = LayoutPlan(
        package=pkg,
        elements=[
            LayoutElement(id="e1", type=ElementType.TEXT, x_mm=20.0, y_mm=20.0, width_mm=20.0, height_mm=5.0),
            LayoutElement(id="e2", type=ElementType.TEXT, x_mm=40.2, y_mm=20.0, width_mm=20.0, height_mm=5.0),
        ],
    )
    res = validate_layout(plan, min_spacing_mm=2.0)
    # Warning or error recorded for spacing violation
    assert len(res.warnings) > 0 or len(res.errors) > 0


# 19. Missing optional medicine information
def test_edge_case_missing_optional_medicine_info():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=90.0,
            package_height_mm=45.0,
            printing_area_width_mm=70.0,
            printing_area_height_mm=35.0,
            printing_area_x_mm=10.0,
            printing_area_y_mm=5.0,
        ),
        tablet=TabletConfig(tablet_count=2, tablet_diameter_mm=8.0),
        information=MedicineInformation(),  # Completely empty optional info
    )
    plan = generate_layout(req)
    assert plan.success is True
    assert len(plan.elements) >= 2


# 20. Large warning and storage text
def test_edge_case_large_warning_storage_text():
    req = make_standard_request(pkg_w=160.0, pkg_h=80.0, print_w=140.0, print_h=65.0)
    req.information.warnings = "WARNING: Keep out of reach of children. Store in a dry place."
    req.information.storage = "Store below 25 deg C away from moisture and direct light."
    plan = generate_layout(req)
    assert plan.success is True
    warn_elem = next((e for e in plan.elements if "warning" in e.id.lower()), None)
    assert warn_elem is not None
    assert "WARNING" in warn_elem.content


# 21. All COST strategy requests
def test_edge_case_all_cost_strategy_requests():
    req = make_standard_request(opt_target="COST")
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True
    assert plan.cost_efficiency is not None
    assert plan.cost_efficiency > 0.0
    assert plan.recommended_strategy == "COST"


# 22. All BALANCED strategy requests
def test_edge_case_all_balanced_strategy_requests():
    req = make_standard_request(opt_target="BALANCED")
    plan = generate_balanced_layout(req)
    assert plan.success is True
    assert plan.balanced_score is not None
    assert plan.balanced_score > 0.0
    assert plan.recommended_strategy == "BALANCED"


# 23. All ACCESSIBILITY strategy requests
def test_edge_case_all_accessibility_strategy_requests():
    req = make_standard_request(opt_target="ACCESSIBILITY")
    plan = generate_accessibility_layout(req)
    assert plan.success is True
    assert plan.accessibility_score is not None
    assert plan.accessibility_score > 0.0
    assert plan.recommended_strategy == "ACCESSIBILITY"


# 24. Full RECOMMEND request
def test_edge_case_full_recommend_request():
    req = make_standard_request(opt_target="RECOMMEND")
    plan = generate_recommendation(req)
    assert plan.success is True
    assert plan.recommended_strategy in ("COST", "BALANCED", "ACCESSIBILITY")
    assert plan.recommended_layout is not None
    assert len(plan.alternatives) == 3
    assert plan.score is not None


# 25. All strategies failing
def test_edge_case_all_strategies_failing():
    # 50 large tablets on a tiny 20x20mm blister
    req = make_standard_request(
        pkg_w=20.0,
        pkg_h=20.0,
        print_w=14.0,
        print_h=14.0,
        margin_x=3.0,
        margin_y=3.0,
        count=50,
        diam=10.0,
    )
    plan = generate_recommendation(req)
    assert plan.success is False
    assert plan.recommended_strategy is None
    assert plan.recommended_layout is None
    assert len(plan.alternatives) == 0
    assert len(plan.errors) > 0


# 26. One strategy failing while others succeed
def test_edge_case_one_strategy_failing_while_others_succeed():
    # Compact layout succeeds under tight space where spacious accessibility is squeezed
    req = make_standard_request(
        pkg_w=60.0,
        pkg_h=35.0,
        print_w=52.0,
        print_h=28.0,
        margin_x=4.0,
        margin_y=3.5,
        count=4,
        diam=8.0,
    )
    plan = generate_recommendation(req)
    assert plan.success is True
    assert len(plan.alternatives) >= 1


# 27. SVG generation from recommendation
def test_edge_case_svg_generation_from_recommendation():
    req = make_standard_request(opt_target="RECOMMEND")
    plan = generate_layout(req)
    svg = render_layout_to_svg(plan)
    assert svg.startswith("<svg")
    assert f'width="{plan.package.package_width_mm}mm"' in svg
    assert f'height="{plan.package.package_height_mm}mm"' in svg
    assert "Amoxicillin" in svg


# 28. PDF generation from recommendation
def test_edge_case_pdf_generation_from_recommendation():
    req = make_standard_request(opt_target="RECOMMEND")
    plan = generate_layout(req)
    pdf = render_layout_to_pdf(plan)
    assert pdf.startswith(b"%PDF-1.4")
    assert pdf.strip().endswith(b"%%EOF")
    assert b"/MediaBox" in pdf


# 29. Invalid API requests
def test_edge_case_invalid_api_requests():
    # Invalid JSON body
    res = client.post("/api/layouts/recommend", content="not json", headers={"Content-Type": "application/json"})
    assert res.status_code == 422
    assert "error" in res.json()

    # Missing mandatory tablet count
    res2 = client.post(
        "/api/layouts/recommend",
        json={
            "package": {
                "package_width_mm": 100.0,
                "package_height_mm": 50.0,
                "printing_area_width_mm": 80.0,
                "printing_area_height_mm": 40.0,
                "printing_area_x_mm": 10.0,
                "printing_area_y_mm": 5.0,
            },
            "tablet": {"tablet_diameter_mm": 9.0},  # Missing tablet_count!
        },
    )
    assert res2.status_code == 422
    assert res2.json()["error"]["code"] == "VALIDATION_ERROR"


# 30. Deterministic repeated requests & Performance Check
def test_edge_case_deterministic_repeated_requests_and_performance():
    req = make_standard_request(opt_target="RECOMMEND")

    start_time = time.perf_counter()
    runs = [generate_layout(req) for _ in range(5)]
    elapsed = time.perf_counter() - start_time

    # Performance: 5 full 3-strategy multi-objective recommendation runs in < 2.0 seconds
    assert elapsed < 2.0

    # Determinism: identical coordinates and scores across all 5 runs
    base_plan = runs[0]
    for other in runs[1:]:
        assert other.score == base_plan.score
        assert other.recommended_strategy == base_plan.recommended_strategy
        assert len(other.elements) == len(base_plan.elements)
        for e1, e2 in zip(base_plan.elements, other.elements):
            assert e1.id == e2.id
            assert e1.x_mm == e2.x_mm
            assert e1.y_mm == e2.y_mm
            assert e1.width_mm == e2.width_mm
            assert e1.height_mm == e2.height_mm

    # Deterministic SVG & PDF output
    svg1 = render_layout_to_svg(base_plan)
    svg2 = render_layout_to_svg(runs[1])
    assert svg1 == svg2

    pdf1 = render_layout_to_pdf(base_plan)
    pdf2 = render_layout_to_pdf(runs[1])
    assert pdf1 == pdf2
