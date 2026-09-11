import pytest
from pydantic import ValidationError

from app.geometry.geometry import mm_to_pixels, pixels_to_mm
from app.models.layout_models import (
    CodeConfig,
    CodeType,
    LayoutRequest,
    MarkingMethod,
    MarkingSide,
    MedicineInformation,
    PackageModel,
    PrintingConstraints,
    TabletCavityPosition,
    TabletConfig,
    TabletMarkingConfig,
)


# 1. Valid package input
def test_valid_package_input():
    pkg = PackageModel(
        package_width_mm=120.0,
        package_height_mm=60.0,
        printing_area_width_mm=100.0,
        printing_area_height_mm=50.0,
        margin_left_mm=10.0,
        margin_right_mm=10.0,
        margin_top_mm=5.0,
        margin_bottom_mm=5.0,
    )
    assert pkg.package_width_mm == 120.0
    assert pkg.package_height_mm == 60.0
    assert pkg.printing_area_width_mm == 100.0
    assert pkg.printing_area_height_mm == 50.0
    assert pkg.printing_area_x_mm == 10.0
    assert pkg.printing_area_y_mm == 5.0


# 2. Invalid package dimensions
def test_invalid_package_dimensions():
    with pytest.raises(ValidationError):
        PackageModel(
            package_width_mm=0.0,  # <= 0 invalid
            package_height_mm=50.0,
            printing_area_width_mm=40.0,
            printing_area_height_mm=30.0,
        )

    with pytest.raises(ValidationError):
        PackageModel(
            package_width_mm=100.0,
            package_height_mm=-10.0,  # negative invalid
            printing_area_width_mm=40.0,
            printing_area_height_mm=30.0,
        )


# 3. Printable area larger than package
def test_printable_area_larger_than_package():
    with pytest.raises(ValidationError) as exc_info:
        PackageModel(
            package_width_mm=80.0,
            package_height_mm=40.0,
            printing_area_width_mm=85.0,  # larger than package width
            printing_area_height_mm=30.0,
        )
    assert "cannot exceed package width" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info2:
        PackageModel(
            package_width_mm=80.0,
            package_height_mm=40.0,
            printing_area_width_mm=70.0,
            printing_area_height_mm=45.0,  # larger than package height
        )
    assert "cannot exceed package height" in str(exc_info2.value)


# 4. Valid tablet configuration (round and non-round)
def test_valid_tablet_configuration():
    # Round tablet
    round_tablet = TabletConfig(tablet_count=10, tablet_diameter_mm=8.5)
    assert round_tablet.tablet_count == 10
    assert round_tablet.tablet_diameter_mm == 8.5
    assert round_tablet.effective_width_mm == 8.5
    assert round_tablet.effective_height_mm == 8.5

    # Non-round / caplet shaped tablet
    caplet = TabletConfig(tablet_count=6, tablet_width_mm=16.0, tablet_height_mm=7.0)
    assert caplet.tablet_count == 6
    assert caplet.effective_width_mm == 16.0
    assert caplet.effective_height_mm == 7.0


# 5. Invalid tablet dimensions
def test_invalid_tablet_dimensions():
    # No dimensions specified
    with pytest.raises(ValidationError) as exc_info:
        TabletConfig(tablet_count=10)
    assert "Tablet dimensions must be specified" in str(exc_info.value)

    # Incomplete non-round dimensions (only width)
    with pytest.raises(ValidationError) as exc_info2:
        TabletConfig(tablet_count=10, tablet_width_mm=12.0)
    assert "Both 'tablet_width_mm' and 'tablet_height_mm' must be provided" in str(exc_info2.value)

    # Negative / zero dimension
    with pytest.raises(ValidationError):
        TabletConfig(tablet_count=10, tablet_diameter_mm=0.0)

    # Tablet count < 1
    with pytest.raises(ValidationError):
        TabletConfig(tablet_count=0, tablet_diameter_mm=8.0)


# 6. Multiple tablet cavities
def test_multiple_tablet_cavities():
    cavities = [
        TabletCavityPosition(id=f"cav_{i+1}", x_mm=10.0 + (i % 5) * 15.0, y_mm=10.0 + (i // 5) * 20.0)
        for i in range(10)
    ]
    tablet_cfg = TabletConfig(
        tablet_count=10,
        tablet_diameter_mm=9.0,
        positions=cavities,
    )
    assert len(tablet_cfg.positions) == 10
    assert tablet_cfg.positions[9].id == "cav_10"


# 7. Human-readable MED001 code
def test_human_readable_med001_code():
    code = CodeConfig(
        code_value="MED001",
        code_type=CodeType.HUMAN_READABLE,
        code_width_mm=25.0,
        code_height_mm=6.0,
        orientation_deg=0.0,
    )
    assert code.code_value == "MED001"
    assert code.value == "MED001"
    assert code.code_type == CodeType.HUMAN_READABLE

    marking = TabletMarkingConfig(
        marking_enabled=True,
        marking_side=MarkingSide.FRONT,
        marking_method=MarkingMethod.INKJET,
        code_value="MED001",
    )
    assert marking.marking_enabled is True
    assert marking.code_value == "MED001"


# 8. Different marking sides
def test_different_marking_sides():
    for side in [MarkingSide.FRONT, MarkingSide.BACK, MarkingSide.BOTH]:
        cfg = TabletMarkingConfig(
            marking_enabled=True,
            marking_side=side,
            code_value="MED001",
        )
        assert cfg.marking_side == side


# 9. Different marking methods
def test_different_marking_methods():
    for method in [
        MarkingMethod.EMBOSS,
        MarkingMethod.DEBOSS,
        MarkingMethod.INKJET,
        MarkingMethod.LASER,
        MarkingMethod.OTHER,
    ]:
        cfg = TabletMarkingConfig(
            marking_enabled=True,
            marking_method=method,
            code_value="MED001",
        )
        assert cfg.marking_method == method


# 10. Invalid code dimensions
def test_invalid_code_dimensions():
    # Negative code width
    with pytest.raises(ValidationError):
        CodeConfig(code_value="MED001", code_width_mm=-10.0)

    # Zero minimum size
    with pytest.raises(ValidationError):
        CodeConfig(code_value="MED001", minimum_code_size_mm=0.0)

    # Empty code string when marking enabled
    with pytest.raises(ValidationError):
        TabletMarkingConfig(marking_enabled=True, code_value="")


# 11. Valid printing constraints
def test_valid_printing_constraints():
    constraints = PrintingConstraints(
        printer_resolution_dpi=600.0,
        minimum_text_size_mm=1.2,
        minimum_element_spacing_mm=0.5,
        minimum_margin_mm=1.5,
    )
    assert constraints.printer_resolution_dpi == 600.0
    assert constraints.minimum_text_size_mm == 1.2
    assert constraints.minimum_element_spacing_mm == 0.5
    assert constraints.minimum_margin_mm == 1.5


# 12. Invalid negative constraints
def test_invalid_negative_constraints():
    with pytest.raises(ValidationError):
        PrintingConstraints(minimum_element_spacing_mm=-1.0)

    with pytest.raises(ValidationError):
        PrintingConstraints(minimum_margin_mm=-0.5)

    with pytest.raises(ValidationError):
        PrintingConstraints(printer_resolution_dpi=0.0)


# 13. Complete layout request
def test_complete_layout_request():
    req = LayoutRequest(
        package=PackageModel(
            package_width_mm=120.0,
            package_height_mm=60.0,
            printing_area_width_mm=100.0,
            printing_area_height_mm=50.0,
            margin_left_mm=10.0,
            margin_right_mm=10.0,
            margin_top_mm=5.0,
            margin_bottom_mm=5.0,
        ),
        tablet=TabletConfig(
            tablet_count=8,
            tablet_diameter_mm=9.0,
            positions=[
                TabletCavityPosition(x_mm=15.0 + i * 12.0, y_mm=25.0)
                for i in range(8)
            ],
        ),
        marking=TabletMarkingConfig(
            marking_enabled=True,
            marking_side=MarkingSide.FRONT,
            marking_method=MarkingMethod.INKJET,
            code_value="MED001",
        ),
        code=CodeConfig(
            code_value="MED001",
            code_type=CodeType.HUMAN_READABLE,
            code_width_mm=20.0,
            code_height_mm=6.0,
        ),
        information=MedicineInformation(
            medicine_name="Paracetamol",
            strength="500mg",
            batch="B1029",
            mfg="2026-01",
            exp="2028-01",
            custom_extra_attr="SPECIAL_GRADE",
        ),
        constraints=PrintingConstraints(
            printer_resolution_dpi=300.0,
            minimum_text_size_mm=1.5,
            minimum_element_spacing_mm=1.0,
            minimum_margin_mm=1.0,
        ),
    )
    assert req.package.package_width_mm == 120.0
    assert req.tablet.tablet_count == 8
    assert req.marking.code_value == "MED001"
    assert req.information.custom_extra_attr == "SPECIAL_GRADE"


# 14. Invalid complete layout request
def test_invalid_complete_layout_request():
    # Cavity position exceeds package width (x=115 + width=9 = 124 > 120)
    with pytest.raises(ValidationError) as exc_info:
        LayoutRequest(
            package=PackageModel(
                package_width_mm=120.0,
                package_height_mm=60.0,
                printing_area_width_mm=100.0,
                printing_area_height_mm=50.0,
                printing_area_x_mm=10.0,
                printing_area_y_mm=5.0,
            ),
            tablet=TabletConfig(
                tablet_count=1,
                tablet_diameter_mm=9.0,
                positions=[TabletCavityPosition(x_mm=115.0, y_mm=20.0)],
            ),
            code=CodeConfig(code_value="MED001"),
        )
    assert "exceeds package width" in str(exc_info.value)


# Unit conversion tests
def test_unit_conversions():
    # 25.4 mm at 300 DPI = exactly 300 pixels
    assert mm_to_pixels(25.4, 300.0) == pytest.approx(300.0)
    # 300 pixels at 300 DPI = exactly 25.4 mm
    assert pixels_to_mm(300.0, 300.0) == pytest.approx(25.4)

    with pytest.raises(ValueError):
        mm_to_pixels(10.0, 0.0)

    with pytest.raises(ValueError):
        pixels_to_mm(100.0, -10.0)
