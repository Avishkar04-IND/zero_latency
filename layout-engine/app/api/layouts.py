from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Response, status

from app.algorithms.placement_engine import generate_layout
from app.models.layout_models import (
    ElementType,
    LayoutElement,
    LayoutPlan,
    LayoutPreviewRequest,
    LayoutRequest,
)
from app.optimizer.optimizer import validate_layout
from app.rendering.pdf_renderer import render_layout_to_pdf
from app.rendering.svg_renderer import render_layout_to_svg

router = APIRouter(prefix="/api/layouts", tags=["layouts"])


def build_baseline_layout(request: LayoutRequest) -> LayoutPlan:
    """Builds an initial baseline layout skeleton from structured layout request parameters."""
    margin = request.min_margin_mm if request.min_margin_mm is not None else request.constraints.minimum_margin_mm
    elements = []

    cavity_w = request.tablet.effective_width_mm or 10.0
    cavity_h = request.tablet.effective_height_mm or 10.0

    if request.tablet.positions:
        for idx, pos in enumerate(request.tablet.positions):
            elements.append(
                LayoutElement(
                    id=pos.id or f"cavity_{idx + 1}",
                    type=ElementType.TABLET_CAVITY,
                    x_mm=pos.x_mm,
                    y_mm=pos.y_mm,
                    width_mm=pos.width_mm or cavity_w,
                    height_mm=pos.height_mm or cavity_h,
                )
            )

    if request.code:
        code_val = request.code.code_value or request.code.value or "MED001"
        code_w = request.code.code_width_mm or request.code.minimum_code_size_mm or 20.0
        code_h = request.code.code_height_mm or 6.0
        elements.append(
            LayoutElement(
                id="code_1",
                type=ElementType.CODE,
                content=code_val,
                x_mm=request.package.printing_area_x_mm + margin,
                y_mm=request.package.printing_area_y_mm + margin,
                width_mm=code_w,
                height_mm=code_h,
                rotation_deg=request.code.orientation_deg,
            )
        )

    if request.information and request.information.medicine_name:
        min_text = request.constraints.minimum_text_size_mm or 2.5
        elements.append(
            LayoutElement(
                id="med_name",
                type=ElementType.TEXT,
                content=request.information.medicine_name,
                x_mm=request.package.printing_area_x_mm + margin,
                y_mm=request.package.printing_area_y_mm + margin + 8.0,
                width_mm=30.0,
                height_mm=4.0,
                font_size_mm=max(min_text, 2.5),
            )
        )

    layout = LayoutPlan(
        id="layout_preview_001",
        package=request.package,
        elements=elements,
    )
    layout.validation = validate_layout(
        layout,
        min_margin_mm=margin,
        min_spacing_mm=request.constraints.minimum_element_spacing_mm,
    )
    return layout


@router.post(
    "/recommend",
    response_model=LayoutPlan,
    summary="Recommend packaging layout",
    description="Validates structured layout input and returns initial layout skeleton.",
)
def recommend_layout(request: LayoutRequest) -> LayoutPlan:
    """Accepts structured layout input and returns a valid deterministic physical layout."""
    return generate_layout(request)


@router.post(
    "/preview",
    summary="Preview packaging layout",
    description="Validates layout and returns rendered SVG and validation report.",
)
def preview_layout(request: LayoutPreviewRequest) -> Dict[str, Any]:
    """Foundational layout preview endpoint supporting LayoutPlan or LayoutRequest."""
    layout = request.layout
    if layout is None and request.request is not None:
        layout = generate_layout(request.request)

    if layout is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No layout provided or generated for preview.",
        )

    if not layout.success:
        return {
            "success": False,
            "layout_id": layout.id,
            "errors": layout.errors,
            "warnings": layout.warnings,
            "validation": (
                layout.validation.model_dump()
                if layout.validation
                else {"valid": False, "errors": layout.errors, "warnings": layout.warnings}
            ),
            "svg": None,
        }

    try:
        svg_content = render_layout_to_svg(layout)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SVG rendering failed: {str(e)}",
        )

    validation = validate_layout(layout)
    return {
        "success": True,
        "layout_id": layout.id,
        "validation": validation.model_dump(),
        "svg": svg_content,
    }


@router.post(
    "/pdf",
    summary="Export packaging layout to PDF",
    description="Renders the physical LayoutPlan to PDF bytes matching package dimensions.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns generated PDF binary stream.",
        },
        400: {"description": "Invalid layout or layout generation failure."},
    },
)
def export_layout_pdf(preview_request: LayoutPreviewRequest):
    """Exports exact physical layout plan to PDF format."""
    layout = preview_request.layout
    if layout is None and preview_request.request is not None:
        layout = generate_layout(preview_request.request)

    if layout is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No layout provided or generated for PDF export.",
        )

    if not layout.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Layout generation failed. Cannot produce physical PDF preview.",
                "errors": layout.errors,
                "warnings": layout.warnings,
            },
        )

    try:
        pdf_bytes = render_layout_to_pdf(layout)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF rendering failed: {str(e)}",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{layout.id}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.get(
    "/{layout_id}",
    response_model=LayoutPlan,
    summary="Get layout by ID",
    description="Foundational endpoint returning layout metadata by ID.",
)
def get_layout(layout_id: str) -> LayoutPlan:
    """Foundational placeholder for retrieving a layout by ID."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Layout '{layout_id}' not found. Persistence is scheduled for future tasks.",
    )
