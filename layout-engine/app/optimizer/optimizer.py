from typing import List, Tuple
from app.geometry.geometry import Rect
from app.models.layout_models import ElementType, LayoutElement, LayoutPlan, ValidationResult


def _element_type_name(elem: LayoutElement) -> str:
    if elem.type == ElementType.TABLET_CAVITY:
        return "Tablet cavity"
    elif elem.type == ElementType.CODE:
        return "Code"
    elif elem.type == ElementType.TEXT:
        return "Text"
    return "Element"


def validate_layout(
    layout: LayoutPlan,
    min_margin_mm: float = 1.0,
    min_spacing_mm: float = 0.0,
) -> ValidationResult:
    """Performs geometric validation, collision detection, boundary, margin, and spacing checks."""
    errors: List[str] = []
    warnings: List[str] = []

    pkg = layout.package
    pkg_rect = Rect(0.0, 0.0, pkg.package_width_mm, pkg.package_height_mm)
    print_rect = Rect(
        pkg.printing_area_x_mm,
        pkg.printing_area_y_mm,
        pkg.printing_area_width_mm,
        pkg.printing_area_height_mm,
    )

    valid_elements: List[Tuple[LayoutElement, Rect]] = []

    for elem in layout.elements:
        if elem.width_mm <= 0.0 or elem.height_mm <= 0.0:
            errors.append(f"Element '{elem.id}' has invalid non-positive dimensions: {elem.width_mm}x{elem.height_mm}mm")
            continue

        elem_rect = Rect(elem.x_mm, elem.y_mm, elem.width_mm, elem.height_mm)
        valid_elements.append((elem, elem_rect))

        # Check package boundary
        if not pkg_rect.contains(elem_rect):
            type_label = _element_type_name(elem)
            errors.append(
                f"{type_label} '{elem.id}' crosses package boundary ({pkg.package_width_mm}x{pkg.package_height_mm}mm)"
            )

        # Check printing area boundary (only text, code, and printed marks must be within printable area)
        if elem.type in (ElementType.TEXT, ElementType.CODE):
            if not print_rect.contains(elem_rect):
                errors.append(f"{_element_type_name(elem)} '{elem.id}' exceeds printable area")
            elif not print_rect.has_min_margin(elem_rect, min_margin_mm):
                warnings.append(
                    f"{_element_type_name(elem)} '{elem.id}' violates minimum {min_margin_mm}mm margin to printing boundary"
                )

    # Collision and spacing detection between all pairs of elements
    for i in range(len(valid_elements)):
        elem_a, rect_a = valid_elements[i]
        type_a = _element_type_name(elem_a)

        for j in range(i + 1, len(valid_elements)):
            elem_b, rect_b = valid_elements[j]
            type_b = _element_type_name(elem_b)

            if rect_a.intersects(rect_b):
                errors.append(f"Collision detected: {type_a} '{elem_a.id}' overlaps {type_b.lower()} '{elem_b.id}'")
            elif min_spacing_mm > 0.0:
                dist = rect_a.distance_to(rect_b)
                if dist < min_spacing_mm:
                    warnings.append(
                        f"Insufficient spacing ({dist:.2f}mm < {min_spacing_mm}mm) between {type_a.lower()} '{elem_a.id}' and {type_b.lower()} '{elem_b.id}'"
                    )

    is_valid = len(errors) == 0
    return ValidationResult(valid=is_valid, errors=errors, warnings=warnings)
