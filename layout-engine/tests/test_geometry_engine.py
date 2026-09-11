import pytest

from app.geometry.geometry import (
    Rect,
    calculate_tablet_marking_area,
    can_fit_in_area,
    compute_bounding_box,
)
from app.models.layout_models import (
    ElementType,
    LayoutElement,
    LayoutPlan,
    PackageModel,
)
from app.optimizer.optimizer import validate_layout


def get_standard_package():
    return PackageModel(
        package_width_mm=120.0,
        package_height_mm=60.0,
        printing_area_width_mm=100.0,
        printing_area_height_mm=50.0,
        margin_left_mm=10.0,
        margin_right_mm=10.0,
        margin_top_mm=5.0,
        margin_bottom_mm=5.0,
    )


# 1. Rectangle area
def test_rectangle_area():
    r1 = Rect(x=5.0, y=10.0, width=20.0, height=15.0)
    assert r1.area == 300.0

    r_zero = Rect(x=0.0, y=0.0, width=0.0, height=10.0)
    assert r_zero.area == 0.0


# 2. Rectangle intersection
def test_rectangle_intersection():
    r1 = Rect(10.0, 10.0, 20.0, 20.0)
    r2 = Rect(20.0, 15.0, 20.0, 20.0)

    # Intersection exists
    inter = r1.intersection(r2)
    assert inter is not None
    assert inter.x == 20.0
    assert inter.y == 15.0
    assert inter.width == 10.0
    assert inter.height == 15.0
    assert inter.area == 150.0

    # No intersection
    r3 = Rect(40.0, 40.0, 10.0, 10.0)
    assert r1.intersection(r3) is None


# 3. Non-overlapping rectangles
def test_non_overlapping_rectangles():
    r1 = Rect(0.0, 0.0, 10.0, 10.0)
    r2 = Rect(15.0, 0.0, 10.0, 10.0)
    r3 = Rect(10.0, 0.0, 10.0, 10.0)  # adjacent edge

    assert r1.intersects(r2) is False
    assert r1.intersects(r3) is False  # touching at edge is not overlapping area
    assert r1.distance_to(r2) == 5.0
    assert r1.distance_to(r3) == 0.0


# 4. Overlapping rectangles
def test_overlapping_rectangles():
    r1 = Rect(10.0, 10.0, 30.0, 20.0)
    r2 = Rect(20.0, 15.0, 30.0, 20.0)
    assert r1.intersects(r2) is True
    assert r2.intersects(r1) is True


# 5. Boundary containment
def test_boundary_containment():
    outer = Rect(0.0, 0.0, 100.0, 50.0)
    inner = Rect(10.0, 10.0, 30.0, 20.0)
    assert outer.contains(inner) is True
    assert inner.contains(outer) is False


# 6. Boundary violation
def test_boundary_violation():
    outer = Rect(0.0, 0.0, 100.0, 50.0)
    exceeds_right = Rect(80.0, 10.0, 30.0, 20.0)  # right edge is 110 > 100
    exceeds_left = Rect(-5.0, 10.0, 20.0, 20.0)

    assert outer.contains(exceeds_right) is False
    assert outer.contains(exceeds_left) is False


# 7. Minimum margin violation
def test_minimum_margin_violation():
    container = Rect(0.0, 0.0, 100.0, 50.0)
    # Element placed at x=1.0 has 1.0mm margin to left, violating 2.0mm minimum margin
    tight_elem = Rect(1.0, 5.0, 20.0, 10.0)
    ok_elem = Rect(5.0, 5.0, 20.0, 10.0)

    assert container.has_min_margin(ok_elem, min_margin=2.0) is True
    assert container.has_min_margin(tight_elem, min_margin=2.0) is False


# 8. Two tablet cavities overlapping
def test_two_tablet_cavities_overlapping():
    pkg = get_standard_package()
    elements = [
        LayoutElement(
            id="cavity_1",
            type=ElementType.TABLET_CAVITY,
            x_mm=20.0,
            y_mm=20.0,
            width_mm=10.0,
            height_mm=10.0,
        ),
        LayoutElement(
            id="cavity_2",
            type=ElementType.TABLET_CAVITY,
            x_mm=25.0,  # overlaps with cavity_1 (20..30)
            y_mm=20.0,
            width_mm=10.0,
            height_mm=10.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan)
    assert result.valid is False
    assert any("Tablet cavity 'cavity_1' overlaps tablet cavity 'cavity_2'" in err for err in result.errors)


# 9. Tablet cavity outside package
def test_tablet_cavity_outside_package():
    pkg = get_standard_package()  # width=120, height=60
    elements = [
        LayoutElement(
            id="cavity_overflow",
            type=ElementType.TABLET_CAVITY,
            x_mm=115.0,  # 115 + 10 = 125 > 120mm
            y_mm=20.0,
            width_mm=10.0,
            height_mm=10.0,
        )
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan)
    assert result.valid is False
    assert any("Tablet cavity 'cavity_overflow' crosses package boundary" in err for err in result.errors)


# 10. Text overlapping code
def test_text_overlapping_code():
    pkg = get_standard_package()
    elements = [
        LayoutElement(
            id="code_1",
            type=ElementType.CODE,
            content="MED001",
            x_mm=20.0,
            y_mm=10.0,
            width_mm=25.0,
            height_mm=8.0,
        ),
        LayoutElement(
            id="text_1",
            type=ElementType.TEXT,
            content="Paracetamol",
            x_mm=30.0,  # overlaps with code (20..45)
            y_mm=12.0,
            width_mm=30.0,
            height_mm=6.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan)
    assert result.valid is False
    assert any("overlaps text 'text_1'" in err or "overlaps code 'code_1'" in err for err in result.errors)


# 11. Code overlapping tablet cavity
def test_code_overlapping_tablet_cavity():
    pkg = get_standard_package()
    elements = [
        LayoutElement(
            id="cavity_1",
            type=ElementType.TABLET_CAVITY,
            x_mm=40.0,
            y_mm=20.0,
            width_mm=12.0,
            height_mm=12.0,
        ),
        LayoutElement(
            id="code_1",
            type=ElementType.CODE,
            content="MED001",
            x_mm=45.0,  # overlaps cavity
            y_mm=22.0,
            width_mm=20.0,
            height_mm=6.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan)
    assert result.valid is False
    assert any("overlaps code 'code_1'" in err or "overlaps tablet cavity 'cavity_1'" in err for err in result.errors)


# 12. Code fitting available area
def test_code_fitting_available_area():
    area = Rect(0.0, 0.0, 10.0, 5.0)
    # code = 8 x 3 mm
    fits, rot = can_fit_in_area(area, item_width_mm=8.0, item_height_mm=3.0)
    assert fits is True
    assert rot == 0.0


# 13. Code not fitting available area
def test_code_not_fitting_available_area():
    area = Rect(0.0, 0.0, 6.0, 3.0)
    # code = 8 x 4 mm -> cannot fit with or without rotation
    fits, _ = can_fit_in_area(area, item_width_mm=8.0, item_height_mm=4.0, allow_rotation=True)
    assert fits is False


# 14. Code fitting after rotation
def test_code_fitting_after_rotation():
    area = Rect(0.0, 0.0, 5.0, 10.0)
    # code = 8 x 3 mm (does not fit horizontally 8 > 5, but fits vertically when rotated 90°: 3 <= 5 and 8 <= 10)
    fits_no_rot, _ = can_fit_in_area(area, item_width_mm=8.0, item_height_mm=3.0, allow_rotation=False)
    assert fits_no_rot is False

    fits_with_rot, rot = can_fit_in_area(area, item_width_mm=8.0, item_height_mm=3.0, allow_rotation=True)
    assert fits_with_rot is True
    assert rot == 90.0


# 15. Minimum spacing violation
def test_minimum_spacing_violation():
    pkg = get_standard_package()
    # Two separate non-overlapping elements with 0.5mm gap
    elements = [
        LayoutElement(
            id="text_1",
            type=ElementType.TEXT,
            content="Batch No",
            x_mm=15.0,
            y_mm=10.0,
            width_mm=20.0,
            height_mm=5.0,
        ),
        LayoutElement(
            id="code_1",
            type=ElementType.CODE,
            content="MED001",
            x_mm=35.5,  # 35.5 - (15.0 + 20.0) = 0.5mm distance
            y_mm=10.0,
            width_mm=20.0,
            height_mm=5.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    # Validate with required 1.0mm minimum spacing -> warning expected
    result = validate_layout(plan, min_spacing_mm=1.0)
    assert result.valid is True  # no collision errors
    assert any("Insufficient spacing" in warn for warn in result.warnings)


# 16. Valid complete layout
def test_valid_complete_layout():
    pkg = get_standard_package()
    # Layout with multiple cavities, batch code, and medicine text with proper spacing & margins
    elements = [
        # Tablet Cavities row
        LayoutElement(
            id=f"cavity_{i+1}",
            type=ElementType.TABLET_CAVITY,
            x_mm=15.0 + i * 15.0,
            y_mm=30.0,
            width_mm=10.0,
            height_mm=10.0,
        )
        for i in range(5)
    ]
    # Human-readable code
    elements.append(
        LayoutElement(
            id="code_batch",
            type=ElementType.CODE,
            content="MED001",
            x_mm=15.0,
            y_mm=10.0,
            width_mm=25.0,
            height_mm=6.0,
        )
    )
    # Medicine text
    elements.append(
        LayoutElement(
            id="med_title",
            type=ElementType.TEXT,
            content="Amoxicillin 500mg",
            x_mm=50.0,
            y_mm=10.0,
            width_mm=45.0,
            height_mm=6.0,
            font_size_mm=3.0,
        )
    )
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan, min_margin_mm=1.0, min_spacing_mm=1.0)
    assert result.valid is True
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
