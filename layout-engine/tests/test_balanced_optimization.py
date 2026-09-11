import pytest

from app.algorithms.placement_engine import (
    calculate_balanced_score,
    generate_balanced_layout,
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


def create_sample_balanced_request(
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
            medicine_name="Paracetamol",
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
        optimization_target="BALANCED",
    )


# 1. Balanced layout generation
def test_balanced_layout_generation():
    req = create_sample_balanced_request()
    plan = generate_balanced_layout(req)
    assert plan.success is True
    assert plan.balanced_score is not None
    assert 0.0 <= plan.balanced_score <= 1.0
    assert len(plan.elements) > 0
    assert plan.id == "layout_balanced_optimized_001"


# 2. Valid collision-free layout
def test_valid_collision_free_layout():
    req = create_sample_balanced_request()
    plan = generate_balanced_layout(req)
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
    req = create_sample_balanced_request()
    plan = generate_balanced_layout(req)
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
    margin = 2.0
    req = create_sample_balanced_request(min_margin=margin)
    plan = generate_balanced_layout(req)
    assert plan.success is True

    pkg = req.package
    min_x = pkg.printing_area_x_mm + margin
    min_y = pkg.printing_area_y_mm + margin
    max_x = pkg.printing_area_x_mm + pkg.printing_area_width_mm - margin
    max_y = pkg.printing_area_y_mm + pkg.printing_area_height_mm - margin

    for e in plan.elements:
        if e.type != ElementType.TABLET_CAVITY:
            assert e.x_mm >= min_x - 1e-4
            assert e.y_mm >= min_y - 1e-4
            assert e.x_mm + e.width_mm <= max_x + 1e-4
            assert e.y_mm + e.height_mm <= max_y + 1e-4


# 5. Space-utilization calculation
def test_space_utilization_calculation():
    elements_tight = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Name", x_mm=10.0, y_mm=10.0, width_mm=20.0, height_mm=5.0),
        LayoutElement(id="t2", type=ElementType.TEXT, content="500mg", x_mm=10.0, y_mm=15.0, width_mm=20.0, height_mm=5.0),
    ]
    _, space_u_tight, _, _, _ = calculate_balanced_score(elements_tight, 100.0, 50.0)
    assert space_u_tight == 1.0

    elements_spaced = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Name", x_mm=10.0, y_mm=10.0, width_mm=20.0, height_mm=5.0),
        LayoutElement(id="t2", type=ElementType.TEXT, content="500mg", x_mm=10.0, y_mm=16.0, width_mm=20.0, height_mm=5.0),
    ]
    _, space_u_spaced, _, _, _ = calculate_balanced_score(elements_spaced, 100.0, 50.0)
    assert 0.0 <= space_u_spaced < 1.0
    assert round(space_u_spaced, 4) == 0.9091


# 6. Readability calculation
def test_readability_calculation():
    elements = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Title", x_mm=10.0, y_mm=10.0, width_mm=25.0, height_mm=6.0, font_size_mm=3.5),
        LayoutElement(id="t2", type=ElementType.TEXT, content="Desc", x_mm=10.0, y_mm=20.0, width_mm=25.0, height_mm=5.0, font_size_mm=3.0),
    ]
    b_score, space_u, read_s, print_e, code_r = calculate_balanced_score(elements, 100.0, 50.0)
    assert 0.0 <= read_s <= 1.0
    # Large font and generous spacing yields strong readability
    assert read_s > 0.8


# 7. Print-efficiency calculation
def test_print_efficiency_calculation():
    elements = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Med", x_mm=10.0, y_mm=10.0, width_mm=20.0, height_mm=10.0),
    ]
    b_score, space_u, read_s, print_e, code_r = calculate_balanced_score(elements, 100.0, 50.0)
    assert 0.0 <= print_e <= 1.0


# 8. Code-reliability calculation
def test_code_reliability_calculation():
    # Code with 0 degree rotation and safe clearance
    elements_0deg = [
        LayoutElement(id="c1", type=ElementType.CODE, content="MED001", x_mm=10.0, y_mm=10.0, width_mm=20.0, height_mm=6.0, rotation_deg=0.0),
        LayoutElement(id="t1", type=ElementType.TEXT, content="Text", x_mm=40.0, y_mm=10.0, width_mm=20.0, height_mm=6.0),
    ]
    _, _, _, _, code_r_0 = calculate_balanced_score(elements_0deg, 100.0, 50.0)

    # Code with 90 degree rotation
    elements_90deg = [
        LayoutElement(id="c1", type=ElementType.CODE, content="MED001", x_mm=10.0, y_mm=10.0, width_mm=6.0, height_mm=20.0, rotation_deg=90.0),
        LayoutElement(id="t1", type=ElementType.TEXT, content="Text", x_mm=40.0, y_mm=10.0, width_mm=20.0, height_mm=6.0),
    ]
    _, _, _, _, code_r_90 = calculate_balanced_score(elements_90deg, 100.0, 50.0)

    assert 0.0 <= code_r_0 <= 1.0
    assert 0.0 <= code_r_90 <= 1.0
    # 0 deg orientation provides higher baseline reliability than rotated
    assert code_r_0 >= code_r_90


# 9. Balanced score calculation
def test_balanced_score_calculation():
    elements = [
        LayoutElement(id="t1", type=ElementType.TEXT, content="Med", x_mm=10.0, y_mm=10.0, width_mm=30.0, height_mm=5.0, font_size_mm=3.0),
        LayoutElement(id="c1", type=ElementType.CODE, content="MED001", x_mm=10.0, y_mm=20.0, width_mm=20.0, height_mm=6.0, rotation_deg=0.0),
    ]
    b_score, space_u, read_s, print_e, code_r = calculate_balanced_score(elements, 100.0, 50.0)
    expected = round(0.30 * space_u + 0.25 * read_s + 0.25 * print_e + 0.20 * code_r, 4)
    assert b_score == pytest.approx(expected, abs=1e-4)


# 10. Multiple candidate evaluation
def test_multiple_candidate_evaluation():
    req = create_sample_balanced_request()
    plan = generate_balanced_layout(req)
    assert plan.success is True
    assert plan.candidates_evaluated is not None
    assert plan.candidates_evaluated >= 2


# 11. Best balanced candidate selection
def test_best_balanced_candidate_selection():
    req = create_sample_balanced_request()
    plan = generate_balanced_layout(req)
    assert plan.success is True
    assert plan.balanced_score is not None
    assert plan.space_utilization is not None
    assert plan.readability is not None
    assert plan.print_efficiency is not None
    assert plan.code_reliability is not None
    assert plan.layout is not None
    assert plan.layout["balanced_score"] == plan.balanced_score


# 12. Impossible layout handling
def test_impossible_layout_handling():
    req = create_sample_balanced_request(
        pkg_w=30.0,
        pkg_h=30.0,
        print_w=20.0,
        print_h=20.0,
        tablet_count=20,
        tablet_diameter=10.0,
        margin_x=2.0,
        margin_y=2.0,
    )
    plan = generate_balanced_layout(req)
    assert plan.success is False
    assert len(plan.elements) == 0
    assert len(plan.errors) > 0


# 13. Deterministic output
def test_deterministic_output():
    req1 = create_sample_balanced_request()
    req2 = create_sample_balanced_request()

    plan1 = generate_balanced_layout(req1)
    plan2 = generate_balanced_layout(req2)

    assert plan1.success is True
    assert plan2.success is True
    assert plan1.balanced_score == plan2.balanced_score
    assert plan1.readability == plan2.readability
    assert len(plan1.elements) == len(plan2.elements)

    for e1, e2 in zip(plan1.elements, plan2.elements):
        assert e1.id == e2.id
        assert e1.x_mm == e2.x_mm
        assert e1.y_mm == e2.y_mm
        assert e1.width_mm == e2.width_mm
        assert e1.height_mm == e2.height_mm
        assert e1.rotation_deg == e2.rotation_deg


# 14. Dispatch via generate_layout with optimization_target="BALANCED"
def test_generate_layout_dispatches_balanced():
    req = create_sample_balanced_request()
    req.optimization_target = "BALANCED"
    plan = generate_layout(req)
    assert plan.success is True
    assert plan.balanced_score is not None
    assert plan.id == "layout_balanced_optimized_001"
