import pytest
from app.algorithms.placement_engine import (
    calculate_cost_efficiency,
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


def create_sample_cost_request(
    pkg_w: float = 120.0,
    pkg_h: float = 60.0,
    print_w: float = 100.0,
    print_h: float = 50.0,
    min_margin: float = 1.0,
    min_spacing: float = 1.0,
    tablet_count: int = 6,
    tablet_diameter: float = 8.0,
    margin_x: float = 5.0,
    margin_y: float = 5.0,
) -> LayoutRequest:
    # Ensure margins fit package
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
        ),
        constraints=PrintingConstraints(
            minimum_margin_mm=min_margin,
            minimum_element_spacing_mm=min_spacing,
        ),
        optimization_target="COST",
    )


# 1. Cost optimization returns a valid layout
def test_cost_optimization_returns_valid_layout():
    req = create_sample_cost_request()
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True
    assert plan.validation is not None
    assert plan.validation.valid is True
    assert len(plan.elements) > 0
    assert plan.cost_efficiency is not None
    assert 0.0 <= plan.cost_efficiency <= 1.0


# 2. Layout remains collision-free
def test_layout_remains_collision_free():
    req = create_sample_cost_request()
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True
    assert len(plan.validation.errors) == 0

    # Explicit collision check between all elements
    for i in range(len(plan.elements)):
        e1 = plan.elements[i]
        for j in range(i + 1, len(plan.elements)):
            e2 = plan.elements[j]
            overlap_x = max(0.0, min(e1.x_mm + e1.width_mm, e2.x_mm + e2.width_mm) - max(e1.x_mm, e2.x_mm))
            overlap_y = max(0.0, min(e1.y_mm + e1.height_mm, e2.y_mm + e2.height_mm) - max(e1.y_mm, e2.y_mm))
            assert overlap_x * overlap_y == 0.0, f"Collision between {e1.id} and {e2.id}"


# 3. Layout remains inside printable area
def test_layout_remains_inside_printable_area():
    req = create_sample_cost_request()
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True

    pkg = req.package
    print_right = pkg.printing_area_x_mm + pkg.printing_area_width_mm
    print_bottom = pkg.printing_area_y_mm + pkg.printing_area_height_mm

    for elem in plan.elements:
        if elem.type != ElementType.TABLET_CAVITY:
            assert elem.x_mm >= pkg.printing_area_x_mm - 1e-4
            assert elem.y_mm >= pkg.printing_area_y_mm - 1e-4
            assert elem.x_mm + elem.width_mm <= print_right + 1e-4
            assert elem.y_mm + elem.height_mm <= print_bottom + 1e-4


# 4. Layout respects margins
def test_layout_respects_margins():
    margin = 2.0
    req = create_sample_cost_request(min_margin=margin)
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True

    pkg = req.package
    min_x = pkg.printing_area_x_mm + margin
    min_y = pkg.printing_area_y_mm + margin
    max_x = pkg.printing_area_x_mm + pkg.printing_area_width_mm - margin
    max_y = pkg.printing_area_y_mm + pkg.printing_area_height_mm - margin

    for elem in plan.elements:
        if elem.type != ElementType.TABLET_CAVITY:
            assert elem.x_mm >= min_x - 1e-4
            assert elem.y_mm >= min_y - 1e-4
            assert elem.x_mm + elem.width_mm <= max_x + 1e-4
            assert elem.y_mm + elem.height_mm <= max_y + 1e-4


# 5. Cost-efficiency calculation
def test_cost_efficiency_calculation():
    # Compactly placed elements
    compact_elements = [
        LayoutElement(id="e1", type=ElementType.TEXT, content="A", x_mm=10.0, y_mm=10.0, width_mm=20.0, height_mm=5.0),
        LayoutElement(id="e2", type=ElementType.TEXT, content="B", x_mm=10.0, y_mm=16.0, width_mm=20.0, height_mm=5.0),
    ]
    eff_compact, used_c, unused_c = calculate_cost_efficiency(compact_elements, 100.0, 50.0)

    # Widely spread elements
    scattered_elements = [
        LayoutElement(id="e1", type=ElementType.TEXT, content="A", x_mm=5.0, y_mm=5.0, width_mm=20.0, height_mm=5.0),
        LayoutElement(id="e2", type=ElementType.TEXT, content="B", x_mm=75.0, y_mm=40.0, width_mm=20.0, height_mm=5.0),
    ]
    eff_scattered, used_s, unused_s = calculate_cost_efficiency(scattered_elements, 100.0, 50.0)

    assert 0.0 <= eff_compact <= 1.0
    assert 0.0 <= eff_scattered <= 1.0
    # Compact layout must yield higher efficiency than scattered layout
    assert eff_compact > eff_scattered


# 6. Unused-area calculation
def test_unused_area_calculation():
    elems = [
        LayoutElement(id="e1", type=ElementType.TEXT, content="A", x_mm=10.0, y_mm=10.0, width_mm=20.0, height_mm=10.0),
    ]
    # Total printable area = 50 * 50 = 2500 mm^2
    # Bounding box = 20 * 10 = 200 mm^2
    # Unused area = 2500 - 200 = 2300 mm^2
    eff, used, unused = calculate_cost_efficiency(elems, 50.0, 50.0)
    assert used == 200.0
    assert unused == 2300.0


# 7. Multiple valid candidates are evaluated
def test_multiple_valid_candidates_are_evaluated():
    req = create_sample_cost_request()
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True
    assert plan.candidates_evaluated is not None
    assert plan.candidates_evaluated >= 2


# 8. Best valid candidate is selected
def test_best_valid_candidate_is_selected():
    req = create_sample_cost_request()
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True
    assert plan.cost_efficiency is not None
    assert plan.used_printable_area is not None
    assert plan.unused_printable_area is not None
    assert plan.used_printable_area + plan.unused_printable_area == pytest.approx(
        req.package.printing_area_width_mm * req.package.printing_area_height_mm, abs=0.1
    )


# 9. Impossible layout returns failure
def test_impossible_layout_returns_failure():
    # Package is 40x40mm with 20 tablets of 15mm diameter (cannot physically fit)
    req = create_sample_cost_request(
        pkg_w=40.0,
        pkg_h=40.0,
        print_w=30.0,
        print_h=30.0,
        tablet_count=20,
        tablet_diameter=15.0,
        margin_x=2.0,
        margin_y=2.0,
    )
    plan = generate_cost_optimized_layout(req)
    assert plan.success is False
    assert len(plan.elements) == 0
    assert len(plan.errors) > 0


# 10. Same input produces the same result (deterministic)
def test_same_input_produces_same_result():
    req1 = create_sample_cost_request()
    req2 = create_sample_cost_request()

    plan1 = generate_cost_optimized_layout(req1)
    plan2 = generate_cost_optimized_layout(req2)

    assert plan1.success is True
    assert plan2.success is True
    assert plan1.cost_efficiency == plan2.cost_efficiency
    assert plan1.used_printable_area == plan2.used_printable_area
    assert plan1.unused_printable_area == plan2.unused_printable_area
    assert len(plan1.elements) == len(plan2.elements)

    for e1, e2 in zip(plan1.elements, plan2.elements):
        assert e1.id == e2.id
        assert e1.x_mm == e2.x_mm
        assert e1.y_mm == e2.y_mm
        assert e1.width_mm == e2.width_mm
        assert e1.height_mm == e2.height_mm
        assert e1.rotation_deg == e2.rotation_deg
