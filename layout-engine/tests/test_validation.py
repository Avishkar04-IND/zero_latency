from app.models.layout_models import (
    ElementType,
    LayoutElement,
    LayoutPlan,
    PackageModel,
)
from app.optimizer.optimizer import validate_layout


def get_base_package():
    return PackageModel(
        package_width_mm=100.0,
        package_height_mm=50.0,
        printing_area_width_mm=80.0,
        printing_area_height_mm=40.0,
        printing_area_x_mm=10.0,
        printing_area_y_mm=5.0,
    )


def test_validation_clean_layout():
    pkg = get_base_package()
    elements = [
        LayoutElement(
            id="text_1",
            type=ElementType.TEXT,
            content="Med A",
            x_mm=12.0,
            y_mm=7.0,
            width_mm=20.0,
            height_mm=10.0,
        ),
        LayoutElement(
            id="code_1",
            type=ElementType.CODE,
            content="MED001",
            x_mm=35.0,
            y_mm=7.0,
            width_mm=20.0,
            height_mm=10.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan, min_margin_mm=1.0)
    assert result.valid is True
    assert len(result.errors) == 0


def test_validation_collision_detected():
    pkg = get_base_package()
    elements = [
        LayoutElement(
            id="text_1",
            type=ElementType.TEXT,
            content="Med A",
            x_mm=15.0,
            y_mm=10.0,
            width_mm=20.0,
            height_mm=10.0,
        ),
        LayoutElement(
            id="code_1",
            type=ElementType.CODE,
            content="MED001",
            x_mm=25.0,  # overlaps with text_1
            y_mm=12.0,
            width_mm=20.0,
            height_mm=10.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan)
    assert result.valid is False
    assert any("Collision detected" in err for err in result.errors)


def test_validation_package_boundary_overflow():
    pkg = get_base_package()
    elements = [
        LayoutElement(
            id="elem_overflow",
            type=ElementType.RECTANGLE,
            x_mm=90.0,
            y_mm=10.0,
            width_mm=20.0,  # 90 + 20 = 110 > 100
            height_mm=10.0,
        )
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan)
    assert result.valid is False
    assert any("package boundary" in err for err in result.errors)


def test_validation_margin_warning():
    pkg = get_base_package()
    # Printing area starts at x=10, so an element at x=10.2 has 0.2mm margin (< 1.0mm)
    elements = [
        LayoutElement(
            id="tight_elem",
            type=ElementType.TEXT,
            content="Close to edge",
            x_mm=10.2,
            y_mm=7.0,
            width_mm=20.0,
            height_mm=10.0,
        )
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    result = validate_layout(plan, min_margin_mm=1.0)
    assert result.valid is True
    assert any("margin" in warn for warn in result.warnings)
