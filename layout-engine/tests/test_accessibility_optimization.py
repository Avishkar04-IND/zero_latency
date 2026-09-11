import pytest

from app.algorithms.placement_engine import (
    calculate_accessibility_score,
    calculate_balanced_score,
    calculate_cost_efficiency,
    generate_accessibility_layout,
    generate_balanced_layout,
    generate_cost_optimized_layout,
    generate_layout,
)
from app.models.layout_models import (
    CodeConfig,
    ElementType,
    LayoutElement,
    LayoutRequest,
    MedicineInformation,
    PackageModel,
    PrintingConstraints,
    TabletConfig,
)


def create_sample_accessibility_request(
    pkg_w: float = 120.0,
    pkg_h: float = 60.0,
    print_w: float = 100.0,
    print_h: float = 50.0,
    min_margin: float = 1.5,
    min_spacing: float = 1.2,
    tablet_count: int = 6,
    tablet_diameter: float = 8.0,
    margin_x: float = 5.0,
    margin_y: float = 5.0,
) -> LayoutRequest:
    actual_mx = min(margin_x, max(0.0, (pkg_w - print_w) / 2.0))
    actual_my = min(margin_y, max(0.0, (pkg_h - print_h) / 2.0))
    return LayoutRequest(
        package=PackageModel(
            package_width_mm=pkg_w,
            package_height_mm=pkg_h,
            printing_area_width_mm=print_w,
            printing_area_height_mm=print_h,
            printing_area_x_mm=actual_mx,
            printing_area_y_mm=actual_my,
            margin_left_mm=actual_mx,
            margin_top_mm=actual_my,
        ),
        tablet=TabletConfig(
            tablet_count=tablet_count,
            tablet_diameter_mm=tablet_diameter,
        ),
        code=CodeConfig(
            code_value="MED001",
            code_width_mm=20.0,
            code_height_mm=6.0,
        ),
        information=MedicineInformation(
            medicine_name="Amoxicillin",
            strength="500 mg",
            batch="B2026",
            mfg="2026-01",
            exp="2028-01",
            warnings="Keep dry",
        ),
        constraints=PrintingConstraints(
            minimum_margin_mm=min_margin,
            minimum_element_spacing_mm=min_spacing,
            minimum_text_size_mm=2.5,
        ),
        optimization_target="ACCESSIBILITY",
    )


# 1. Accessibility layout generation
def test_accessibility_layout_generation():
    req = create_sample_accessibility_request()
    plan = generate_accessibility_layout(req)
    assert plan.success is True
    assert plan.accessibility_score is not None
    assert 0.0 <= plan.accessibility_score <= 1.0
    assert len(plan.elements) > 0
    assert plan.id == "layout_accessibility_optimized_001"


# 2. Valid collision-free layout
def test_valid_collision_free_layout():
    req = create_sample_accessibility_request()
    plan = generate_accessibility_layout(req)
    assert plan.success is True
    assert plan.validation.valid is True
    assert len(plan.validation.errors) == 0

    # Ensure no element overlaps another
    for i in range(len(plan.elements)):
        e1 = plan.elements[i]
        for j in range(i + 1, len(plan.elements)):
            e2 = plan.elements[j]
            overlap_x = max(0.0, min(e1.x_mm + e1.width_mm, e2.x_mm + e2.width_mm) - max(e1.x_mm, e2.x_mm))
            overlap_y = max(0.0, min(e1.y_mm + e1.height_mm, e2.y_mm + e2.height_mm) - max(e1.y_mm, e2.y_mm))
            assert overlap_x * overlap_y == 0.0, f"Collision between {e1.id} and {e2.id}"


# 3. Printable-area compliance
def test_printable_area_compliance():
    req = create_sample_accessibility_request()
    plan = generate_accessibility_layout(req)
    assert plan.success is True

    pkg = req.package
    print_right = pkg.printing_area_x_mm + pkg.printing_area_width_mm
    print_bottom = pkg.printing_area_y_mm + pkg.printing_area_height_mm

    for e in plan.elements:
        if e.type != ElementType.TABLET_CAVITY:
            assert e.x_mm >= pkg.printing_area_x_mm - 1e-4
            assert e.y_mm >= pkg.printing_area_y_mm - 1e-4
            assert e.x_mm + e.width_mm <= print_right + 1e-4
            assert e.y_mm + e.height_mm <= print_bottom + 1e-4


# 4. Margin compliance
def test_margin_compliance():
    req = create_sample_accessibility_request(min_margin=2.0)
    plan = generate_accessibility_layout(req)
    assert plan.success is True

    pkg = req.package
    min_m = req.constraints.minimum_margin_mm
    min_x = pkg.printing_area_x_mm + min_m
    min_y = pkg.printing_area_y_mm + min_m
    max_x = pkg.printing_area_x_mm + pkg.printing_area_width_mm - min_m
    max_y = pkg.printing_area_y_mm + pkg.printing_area_height_mm - min_m

    for e in plan.elements:
        if e.type != ElementType.TABLET_CAVITY:
            assert e.x_mm >= min_x - 1e-4
            assert e.y_mm >= min_y - 1e-4
            assert e.x_mm + e.width_mm <= max_x + 1e-4
            assert e.y_mm + e.height_mm <= max_y + 1e-4


# 5. Accessibility score calculation
def test_accessibility_score_calculation():
    elements = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Title", x_mm=10.0, y_mm=10.0, width_mm=25.0, height_mm=5.0, font_size_mm=3.2),
        LayoutElement(id="t2", type=ElementType.TEXT, content="Batch", x_mm=10.0, y_mm=20.0, width_mm=20.0, height_mm=4.0, font_size_mm=2.5),
        LayoutElement(id="c1", type=ElementType.CODE, content="MED001", x_mm=50.0, y_mm=10.0, width_mm=20.0, height_mm=6.0, rotation_deg=0.0),
    ]
    acc_score, read_s, space_q, white_q, code_r = calculate_accessibility_score(elements, 100.0, 50.0)
    assert 0.0 <= acc_score <= 1.0
    expected = round(0.35 * read_s + 0.25 * space_q + 0.20 * white_q + 0.20 * code_r, 4)
    assert acc_score == expected


# 6. Readability metric
def test_readability_metric():
    # Larger fonts and generous bounding boxes produce higher readability
    elements_large = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Name", x_mm=10.0, y_mm=10.0, width_mm=30.0, height_mm=5.0, font_size_mm=3.5),
    ]
    elements_small = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Name", x_mm=10.0, y_mm=10.0, width_mm=15.0, height_mm=2.5, font_size_mm=1.5),
    ]
    _, read_large, _, _, _ = calculate_accessibility_score(elements_large, 100.0, 50.0)
    _, read_small, _, _, _ = calculate_accessibility_score(elements_small, 100.0, 50.0)
    assert read_large > read_small


# 7. Spacing quality
def test_spacing_quality():
    # Spaced apart elements produce higher spacing quality
    elements_spaced = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="A", x_mm=10.0, y_mm=10.0, width_mm=10.0, height_mm=5.0),
        LayoutElement(id="t2", type=ElementType.TEXT, content="B", x_mm=50.0, y_mm=10.0, width_mm=10.0, height_mm=5.0),
    ]
    elements_tight = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="A", x_mm=10.0, y_mm=10.0, width_mm=10.0, height_mm=5.0),
        LayoutElement(id="t2", type=ElementType.TEXT, content="B", x_mm=21.0, y_mm=10.0, width_mm=10.0, height_mm=5.0),
    ]
    _, _, space_q_spaced, _, _ = calculate_accessibility_score(elements_spaced, 100.0, 50.0)
    _, _, space_q_tight, _, _ = calculate_accessibility_score(elements_tight, 100.0, 50.0)
    assert space_q_spaced > space_q_tight


# 8. Whitespace quality
def test_whitespace_quality():
    # Low element coverage yields higher whitespace quality
    elements_few = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Name", x_mm=10.0, y_mm=10.0, width_mm=10.0, height_mm=5.0),
    ]
    elements_crowded = [
        LayoutElement(id=f"t{i}", type=ElementType.TEXT, content=f"Text{i}", x_mm=10.0 + (i % 3) * 25, y_mm=5.0 + (i // 3) * 10, width_mm=20.0, height_mm=8.0)
        for i in range(12)
    ]
    _, _, _, white_few, _ = calculate_accessibility_score(elements_few, 100.0, 50.0)
    _, _, _, white_crowded, _ = calculate_accessibility_score(elements_crowded, 100.0, 50.0)
    assert white_few > white_crowded


# 9. Code reliability
def test_code_reliability():
    # 0 deg rotation and ample clearance yields higher code reliability
    elements_ideal = [
        LayoutElement(id="c1", type=ElementType.CODE, content="MED001", x_mm=10.0, y_mm=10.0, width_mm=20.0, height_mm=6.0, rotation_deg=0.0),
        LayoutElement(id="t1", type=ElementType.TEXT, content="Name", x_mm=50.0, y_mm=10.0, width_mm=20.0, height_mm=5.0),
    ]
    elements_rotated = [
        LayoutElement(id="c1", type=ElementType.CODE, content="MED001", x_mm=10.0, y_mm=10.0, width_mm=6.0, height_mm=20.0, rotation_deg=90.0),
        LayoutElement(id="t1", type=ElementType.TEXT, content="Name", x_mm=50.0, y_mm=10.0, width_mm=20.0, height_mm=5.0),
    ]
    _, _, _, _, code_r_ideal = calculate_accessibility_score(elements_ideal, 100.0, 50.0)
    _, _, _, _, code_r_rotated = calculate_accessibility_score(elements_rotated, 100.0, 50.0)
    assert code_r_ideal > code_r_rotated


# 10. Multiple candidate evaluation
def test_multiple_candidate_evaluation():
    req = create_sample_accessibility_request()
    plan = generate_accessibility_layout(req)
    assert plan.candidates_evaluated is not None
    assert plan.candidates_evaluated >= 2


# 11. Highest accessibility candidate selection
def test_highest_accessibility_candidate_selection():
    req = create_sample_accessibility_request()
    plan = generate_accessibility_layout(req)
    assert plan.success is True
    assert plan.accessibility_score is not None
    assert plan.readability is not None
    assert plan.spacing_quality is not None
    assert plan.whitespace_quality is not None
    assert plan.code_reliability is not None
    assert plan.layout is not None
    assert plan.layout["accessibility_score"] == plan.accessibility_score
    assert plan.layout["spacing_quality"] == plan.spacing_quality
    assert plan.layout["whitespace_quality"] == plan.whitespace_quality


# 12. Impossible layout handling
def test_impossible_layout_handling():
    req = create_sample_accessibility_request(
        pkg_w=30.0,
        pkg_h=30.0,
        print_w=20.0,
        print_h=20.0,
        tablet_count=20,
        tablet_diameter=10.0,
        margin_x=2.0,
        margin_y=2.0,
    )
    plan = generate_accessibility_layout(req)
    assert plan.success is False
    assert len(plan.elements) == 0
    assert len(plan.errors) > 0


# 13. Deterministic output
def test_deterministic_output():
    req = create_sample_accessibility_request()
    plan1 = generate_accessibility_layout(req)
    plan2 = generate_accessibility_layout(req)

    assert plan1.success is True
    assert plan2.success is True
    assert plan1.accessibility_score == plan2.accessibility_score
    assert len(plan1.elements) == len(plan2.elements)
    for e1, e2 in zip(plan1.elements, plan2.elements):
        assert e1.id == e2.id
        assert e1.x_mm == e2.x_mm
        assert e1.y_mm == e2.y_mm
        assert e1.width_mm == e2.width_mm
        assert e1.height_mm == e2.height_mm


# 14. Existing cost optimization still works
def test_existing_cost_optimization_still_works():
    req = create_sample_accessibility_request()
    req.optimization_target = "COST"
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True
    assert plan.cost_efficiency is not None
    assert plan.used_printable_area is not None
    assert plan.unused_printable_area is not None


# 15. Existing balanced optimization still works
def test_existing_balanced_optimization_still_works():
    req = create_sample_accessibility_request()
    req.optimization_target = "BALANCED"
    plan = generate_balanced_layout(req)
    assert plan.success is True
    assert plan.balanced_score is not None
    assert plan.space_utilization is not None
    assert plan.readability is not None


# 16. Endpoint dispatch for accessibility target
def test_generate_layout_dispatches_accessibility():
    req = create_sample_accessibility_request()
    req.optimization_target = "ACCESSIBILITY"
    plan = generate_layout(req)
    assert plan.success is True
    assert plan.id == "layout_accessibility_optimized_001"
    assert plan.accessibility_score is not None
