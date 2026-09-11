import pytest
from pydantic import ValidationError
from app.models.layout_models import (
    CodeConfig,
    CodeType,
    ElementType,
    LayoutElement,
    LayoutPlan,
    MedicineInformation,
    PackageModel,
    TabletConfig,
    TabletPosition,
    ValidationResult,
)


def test_package_model_valid():
    pkg = PackageModel(
        package_width_mm=100.0,
        package_height_mm=50.0,
        printing_area_width_mm=80.0,
        printing_area_height_mm=40.0,
        printing_area_x_mm=10.0,
        printing_area_y_mm=5.0,
    )
    assert pkg.package_width_mm == 100.0
    assert pkg.printing_area_width_mm == 80.0


def test_package_model_invalid_dimensions():
    with pytest.raises(ValidationError):
        PackageModel(
            package_width_mm=-10.0,
            package_height_mm=50.0,
            printing_area_width_mm=40.0,
            printing_area_height_mm=20.0,
        )


def test_package_model_printing_area_exceeds_bounds():
    with pytest.raises(ValidationError):
        PackageModel(
            package_width_mm=100.0,
            package_height_mm=50.0,
            printing_area_width_mm=95.0,
            printing_area_height_mm=40.0,
            printing_area_x_mm=10.0,  # 10 + 95 > 100
            printing_area_y_mm=5.0,
        )


def test_tablet_config():
    config = TabletConfig(
        tablet_count=10,
        tablet_diameter_mm=8.0,
        positions=[TabletPosition(x_mm=10.0, y_mm=10.0)],
    )
    assert config.tablet_count == 10
    assert len(config.positions) == 1

    with pytest.raises(ValidationError):
        TabletConfig(tablet_count=0)


def test_code_config():
    code = CodeConfig(value="MED001", code_type=CodeType.HUMAN_READABLE)
    assert code.value == "MED001"
    assert code.code_type == CodeType.HUMAN_READABLE

    with pytest.raises(ValidationError):
        CodeConfig(value="")


def test_medicine_information_extensible():
    info = MedicineInformation(
        medicine_name="Paracetamol",
        strength="500mg",
        batch="B2026",
        custom_regulatory_flag="REG-EU-01",
    )
    assert info.medicine_name == "Paracetamol"
    assert getattr(info, "custom_regulatory_flag") == "REG-EU-01"


def test_layout_element():
    elem = LayoutElement(
        id="elem_1",
        type=ElementType.TEXT,
        content="Paracetamol 500mg",
        x_mm=5.0,
        y_mm=5.0,
        width_mm=30.0,
        height_mm=5.0,
        font_size_mm=2.5,
    )
    assert elem.id == "elem_1"
    assert elem.width_mm == 30.0
