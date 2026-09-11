from app.models.layout_models import (
    ElementType,
    LayoutElement,
    LayoutPlan,
    PackageModel,
)
from app.rendering.svg_renderer import render_layout_to_svg


def test_svg_rendering_basic():
    pkg = PackageModel(
        package_width_mm=120.0,
        package_height_mm=60.0,
        printing_area_width_mm=100.0,
        printing_area_height_mm=50.0,
        printing_area_x_mm=10.0,
        printing_area_y_mm=5.0,
    )
    elements = [
        LayoutElement(
            id="cavity_1",
            type=ElementType.TABLET_CAVITY,
            x_mm=15.0,
            y_mm=10.0,
            width_mm=10.0,
            height_mm=10.0,
        ),
        LayoutElement(
            id="code_1",
            type=ElementType.CODE,
            content="MED001 & BATCH",
            x_mm=30.0,
            y_mm=10.0,
            width_mm=25.0,
            height_mm=6.0,
        ),
        LayoutElement(
            id="text_1",
            type=ElementType.TEXT,
            content="Aspirin <500mg>",
            x_mm=30.0,
            y_mm=20.0,
            width_mm=40.0,
            height_mm=5.0,
        ),
    ]
    plan = LayoutPlan(package=pkg, elements=elements)
    svg = render_layout_to_svg(plan)

    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert 'width="120.0mm"' in svg
    assert 'height="60.0mm"' in svg
    assert 'viewBox="0 0 120.0 60.0"' in svg
    assert 'class="package-boundary"' in svg
    assert 'class="print-area"' in svg
    assert 'class="tablet-cavity"' in svg
    assert 'id="cavity_1"' in svg
    # XML escaping verification
    assert "MED001 &amp; BATCH" in svg
    assert "Aspirin &lt;500mg&gt;" in svg
