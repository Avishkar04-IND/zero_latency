import pytest
from app.algorithms.placement_engine import generate_layout
from app.models.layout_models import (
    CodeConfig,
    CodeType,
    ElementType,
    LayoutRequest,
    MedicineInformation,
    PackageModel,
    PrintingConstraints,
    TabletCavityPosition,
    TabletConfig,
    TabletMarkingConfig,
)


def create_base_request(
    pkg_w: float = 120.0,
    pkg_h: float = 60.0,
    print_w: float = 100.0,
    print_h: float = 50.0,
    margin_x: float = 10.0,
    margin_y: float = 5.0,
    tablet_count: int = 10,
    tablet_diameter: float = 8.0,
    positions=None,
    medicine_name="Amoxicillin",
    strength="500mg",
    batch="B2026",
    mfg="2026-01",
    exp="2028-01",
    code_val="MED001",
    min_margin: float = 1.0,
    min_spacing: float = 1.0,
) -> LayoutRequest:
    return LayoutRequest(
        package=PackageModel(
            package_width_mm=pkg_w,
            package_height_mm=pkg_h,
            printing_area_width_mm=print_w,
            printing_area_height_mm=print_h,
            printing_area_x_mm=margin_x,
            printing_area_y_mm=margin_y,
            margin_left_mm=margin_x,
            margin_top_mm=margin_y,
        ),
        tablet=TabletConfig(
            tablet_count=tablet_count,
            tablet_diameter_mm=tablet_diameter,
            positions=positions,
        ),
        code=CodeConfig(code_value=code_val) if code_val else None,
        information=MedicineInformation(
            medicine_name=medicine_name,
            strength=strength,
            batch=batch,
            mfg=mfg,
            exp=exp,
        ),
        constraints=PrintingConstraints(
            minimum_margin_mm=min_margin,
            minimum_element_spacing_mm=min_spacing,
        ),
    )


# 1. Basic valid package layout
def test_basic_valid_package_layout():
    req = create_base_request()
    plan = generate_layout(req)
    assert plan.success is True
    assert plan.validation is not None
    assert plan.validation.valid is True
    assert len(plan.elements) > 0


# 2. Medicine name placement
def test_medicine_name_placement():
    req = create_base_request(medicine_name="Paracetamol Special", strength=None, batch=None, mfg=None, exp=None)
    plan = generate_layout(req)
    assert plan.success is True
    med_elements = [e for e in plan.elements if e.id == "med_name"]
    assert len(med_elements) == 1
    assert med_elements[0].content == "Paracetamol Special"
    assert med_elements[0].type == ElementType.TEXT


# 3. Strength placement
def test_strength_placement():
    req = create_base_request(medicine_name="Ibuprofen", strength="400 mg", batch=None, mfg=None, exp=None)
    plan = generate_layout(req)
    assert plan.success is True
    str_elements = [e for e in plan.elements if e.id == "med_strength"]
    assert len(str_elements) == 1
    assert str_elements[0].content == "400 mg"


# 4. Batch/MFG/EXP placement
def test_batch_mfg_exp_placement():
    req = create_base_request(batch="BAT-999", mfg="03/2026", exp="03/2029")
    plan = generate_layout(req)
    assert plan.success is True
    elem_ids = {e.id for e in plan.elements}
    assert "batch_no" in elem_ids
    assert "mfg_date" in elem_ids
    assert "exp_date" in elem_ids


# 5. Code placement
def test_code_placement():
    req = create_base_request(code_val="MED-ALPHA-01")
    plan = generate_layout(req)
    assert plan.success is True
    code_elems = [e for e in plan.elements if e.type == ElementType.CODE]
    assert len(code_elems) == 1
    assert code_elems[0].content == "MED-ALPHA-01"


# 6. Multiple medicine information fields
def test_multiple_medicine_information_fields():
    req = create_base_request()
    req.information.ingredients = "Active Ingredient 500mg"
    req.information.manufacturer = "PharmaCorp Ltd"
    req.information.mrp = "150.00"
    req.information.warnings = "Keep away from children"
    plan = generate_layout(req)
    assert plan.success is True
    elem_ids = {e.id for e in plan.elements}
    assert "ingredients" in elem_ids
    assert "manufacturer" in elem_ids
    assert "mrp" in elem_ids
    assert "warnings" in elem_ids


# 7. Multiple tablet cavities
def test_multiple_tablet_cavities():
    req = create_base_request(tablet_count=8, tablet_diameter=7.0)
    plan = generate_layout(req)
    assert plan.success is True
    cavities = [e for e in plan.elements if e.type == ElementType.TABLET_CAVITY]
    assert len(cavities) == 8


# 8. Automatic tablet arrangement
def test_automatic_tablet_arrangement():
    # 6 tablets with no positions supplied
    req = create_base_request(tablet_count=6, tablet_diameter=8.0, positions=None)
    plan = generate_layout(req)
    assert plan.success is True
    cavities = [e for e in plan.elements if e.type == ElementType.TABLET_CAVITY]
    assert len(cavities) == 6
    # Verify no cavities collide
    for i in range(len(cavities)):
        for j in range(i + 1, len(cavities)):
            c1 = cavities[i]
            c2 = cavities[j]
            # Must not overlap
            overlap_x = max(0.0, min(c1.x_mm + c1.width_mm, c2.x_mm + c2.width_mm) - max(c1.x_mm, c2.x_mm))
            overlap_y = max(0.0, min(c1.y_mm + c1.height_mm, c2.y_mm + c2.height_mm) - max(c1.y_mm, c2.y_mm))
            assert overlap_x * overlap_y == 0.0


# 9. Supplied tablet positions
def test_supplied_tablet_positions():
    supplied = [
        TabletCavityPosition(id="cav_fixed_1", x_mm=20.0, y_mm=25.0),
        TabletCavityPosition(id="cav_fixed_2", x_mm=40.0, y_mm=25.0),
    ]
    req = create_base_request(tablet_count=2, positions=supplied)
    plan = generate_layout(req)
    assert plan.success is True
    cavities = {e.id: e for e in plan.elements if e.type == ElementType.TABLET_CAVITY}
    assert "cav_fixed_1" in cavities
    assert cavities["cav_fixed_1"].x_mm == 20.0
    assert cavities["cav_fixed_1"].y_mm == 25.0
    assert "cav_fixed_2" in cavities
    assert cavities["cav_fixed_2"].x_mm == 40.0


# 10. Collision-free placement
def test_collision_free_placement():
    req = create_base_request()
    plan = generate_layout(req)
    assert plan.success is True
    assert len(plan.validation.errors) == 0


# 11. Margin compliance
def test_margin_compliance():
    min_margin = 2.0
    req = create_base_request(min_margin=min_margin)
    plan = generate_layout(req)
    assert plan.success is True
    pkg = req.package
    print_right = pkg.printing_area_x_mm + pkg.printing_area_width_mm
    print_bottom = pkg.printing_area_y_mm + pkg.printing_area_height_mm
    for e in plan.elements:
        if e.type != ElementType.TABLET_CAVITY:
            assert e.x_mm >= pkg.printing_area_x_mm + min_margin - 1e-4
            assert e.y_mm >= pkg.printing_area_y_mm + min_margin - 1e-4
            assert e.x_mm + e.width_mm <= print_right - min_margin + 1e-4
            assert e.y_mm + e.height_mm <= print_bottom - min_margin + 1e-4


# 12. Printable-area compliance
def test_printable_area_compliance():
    req = create_base_request()
    plan = generate_layout(req)
    assert plan.success is True
    pkg = req.package
    for e in plan.elements:
        if e.type != ElementType.TABLET_CAVITY:
            assert e.x_mm >= pkg.printing_area_x_mm
            assert e.y_mm >= pkg.printing_area_y_mm
            assert e.x_mm + e.width_mm <= pkg.printing_area_x_mm + pkg.printing_area_width_mm + 1e-4
            assert e.y_mm + e.height_mm <= pkg.printing_area_y_mm + pkg.printing_area_height_mm + 1e-4


# 13. Code rotation when necessary
def test_code_rotation_when_necessary():
    # Narrow vertical printing area: width=12mm, height=50mm
    # Code dimensions: 25mm wide x 6mm high
    # Cannot fit at 0°, must rotate 90° or 270° (6mm wide x 25mm high)
    req = create_base_request(
        pkg_w=60.0,
        pkg_h=80.0,
        print_w=15.0,
        print_h=60.0,
        margin_x=5.0,
        margin_y=5.0,
        tablet_count=2,
        tablet_diameter=5.0,
        medicine_name=None,
        strength=None,
        batch=None,
        mfg=None,
        exp=None,
    )
    req.code = CodeConfig(
        code_value="MED001",
        code_width_mm=25.0,
        code_height_mm=6.0,
        orientation_deg=0.0,
    )
    plan = generate_layout(req)
    assert plan.success is True
    code_elem = [e for e in plan.elements if e.type == ElementType.CODE][0]
    assert code_elem.rotation_deg in (90.0, 270.0)


# 14. Insufficient printable area
def test_insufficient_printable_area():
    # Extremely small printable area (4mm x 4mm) with 1mm margin -> 2x2mm usable
    # Medicine text requires much more than 2x2mm
    req = create_base_request(
        pkg_w=50.0,
        pkg_h=50.0,
        print_w=4.0,
        print_h=4.0,
        margin_x=2.0,
        margin_y=2.0,
        medicine_name="Paracetamol Extra Strength",
    )
    plan = generate_layout(req)
    assert plan.success is False
    assert len(plan.elements) == 0
    assert any("insufficient printable area" in err.lower() for err in plan.errors)


# 15. Impossible tablet arrangement
def test_impossible_tablet_arrangement():
    # Package is 20x20mm, but requests 50 tablets of 10mm diameter
    req = create_base_request(
        pkg_w=20.0,
        pkg_h=20.0,
        print_w=15.0,
        print_h=15.0,
        margin_x=2.0,
        margin_y=2.0,
        tablet_count=50,
        tablet_diameter=10.0,
    )
    plan = generate_layout(req)
    assert plan.success is False
    assert any("impossible tablet arrangement" in err.lower() for err in plan.errors)


# 16. Impossible code placement
def test_impossible_code_placement():
    # Package 40x40mm, code is 35x25mm, plus 4 tablets taking all room
    req = create_base_request(
        pkg_w=40.0,
        pkg_h=40.0,
        print_w=30.0,
        print_h=30.0,
        margin_x=5.0,
        margin_y=5.0,
        tablet_count=4,
        tablet_diameter=12.0,
        medicine_name=None,
        strength=None,
        batch=None,
        mfg=None,
        exp=None,
    )
    req.code = CodeConfig(
        code_value="HUGE_CODE_999",
        code_width_mm=28.0,
        code_height_mm=28.0,
    )
    plan = generate_layout(req)
    assert plan.success is False
    assert any("insufficient printable area" in err.lower() for err in plan.errors)


# 17. Deterministic result — same input produces same output
def test_deterministic_result_same_input_same_output():
    req1 = create_base_request(medicine_name="Amoxicillin", strength="250mg", batch="B123")
    req2 = create_base_request(medicine_name="Amoxicillin", strength="250mg", batch="B123")

    plan1 = generate_layout(req1)
    plan2 = generate_layout(req2)

    assert plan1.success is True
    assert plan2.success is True
    assert len(plan1.elements) == len(plan2.elements)

    for e1, e2 in zip(plan1.elements, plan2.elements):
        assert e1.id == e2.id
        assert e1.x_mm == e2.x_mm
        assert e1.y_mm == e2.y_mm
        assert e1.width_mm == e2.width_mm
        assert e1.height_mm == e2.height_mm
        assert e1.rotation_deg == e2.rotation_deg


# 18. Complete valid medicine package layout
def test_complete_valid_medicine_package_layout():
    req = create_base_request(
        pkg_w=140.0,
        pkg_h=70.0,
        print_w=120.0,
        print_h=60.0,
        margin_x=10.0,
        margin_y=5.0,
        tablet_count=10,
        tablet_diameter=8.0,
        medicine_name="Metformin HCl",
        strength="850 mg",
        batch="MF-2026-08",
        mfg="08/2026",
        exp="07/2029",
        code_val="MED001",
    )
    req.information.manufacturer = "Sunrise Pharma Ltd"
    req.information.warnings = "Store below 25°C"
    req.information.mrp = "45.00"

    plan = generate_layout(req)
    assert plan.success is True
    assert plan.validation.valid is True
    assert len(plan.elements) >= 15  # 10 cavities + name + strength + batch + mfg + exp + code + ...
    assert plan.layout is not None
    assert plan.layout["package_width_mm"] == 140.0
