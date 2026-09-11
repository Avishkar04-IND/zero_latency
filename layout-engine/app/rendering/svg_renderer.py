import html
from typing import List, Optional

from app.models.layout_models import CodeType, ElementType, LayoutPlan


def render_layout_to_svg(layout: LayoutPlan) -> str:
    """Generates production-oriented valid standalone SVG markup representing a packaging layout in millimeters.
    Preserves physical aspect ratio and visually renders package boundary, printable area,
    round/non-round tablet cavities, text elements, and human-readable or reserved code areas.
    """
    if layout is None:
        raise ValueError("Cannot render SVG: LayoutPlan is None.")
    if layout.package is None:
        raise ValueError("Cannot render SVG: LayoutPlan missing package information.")
    if not layout.success:
        err_msg = "; ".join(layout.errors) if layout.errors else "Layout generation was unsuccessful"
        raise ValueError(f"Cannot render SVG: {err_msg}")

    pkg = layout.package
    w = pkg.package_width_mm
    h = pkg.package_height_mm

    if w <= 0 or h <= 0:
        raise ValueError(f"Cannot render SVG: Invalid package dimensions ({w}x{h}mm).")

    svg_lines: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
        '  <style>',
        '    .package-boundary { fill: #ffffff; stroke: #1e293b; stroke-width: 0.5; }',
        '    .print-area { fill: #f8fafc; stroke: #94a3b8; stroke-width: 0.3; stroke-dasharray: 1, 1; }',
        '    .tablet-cavity { fill: #e2e8f0; stroke: #64748b; stroke-width: 0.3; }',
        '    .layout-code { fill: #f1f5f9; stroke: #0284c7; stroke-width: 0.3; }',
        '    .code-reserved-datamatrix { fill: #eff6ff; stroke: #2563eb; stroke-width: 0.35; stroke-dasharray: 1.5, 1; }',
        '    .code-reserved-qr { fill: #eff6ff; stroke: #2563eb; stroke-width: 0.35; stroke-dasharray: 1.5, 1; }',
        '    .code-reserved-barcode { fill: #eff6ff; stroke: #2563eb; stroke-width: 0.35; stroke-dasharray: 2, 1; }',
        '    .layout-rect { fill: none; stroke: #cbd5e1; stroke-width: 0.2; }',
        '    .layout-text { font-family: sans-serif; fill: #0f172a; dominant-baseline: hanging; }',
        '    .layout-code-text { font-family: monospace; font-size: 2mm; fill: #0369a1; }',
        '    .layout-code-reserved-text { font-family: monospace; font-size: 1.8mm; fill: #1d4ed8; font-weight: bold; }',
        '  </style>',
        f'  <rect class="package-boundary" x="0" y="0" width="{w}" height="{h}" rx="1" ry="1" />',
        f'  <rect class="print-area" x="{pkg.printing_area_x_mm}" y="{pkg.printing_area_y_mm}" '
        f'width="{pkg.printing_area_width_mm}" height="{pkg.printing_area_height_mm}" />',
    ]

    for elem in layout.elements:
        escaped_content = html.escape(elem.content or "")
        transform = ""
        cx = elem.x_mm + elem.width_mm / 2.0
        cy = elem.y_mm + elem.height_mm / 2.0
        if elem.rotation_deg:
            transform = f' transform="rotate({elem.rotation_deg} {cx} {cy})"'

        if elem.type == ElementType.TABLET_CAVITY:
            # Render round tablets as circles, non-round as bounding rect
            if abs(elem.width_mm - elem.height_mm) < 1e-4:
                r = elem.width_mm / 2.0
                svg_lines.append(
                    f'  <circle class="tablet-cavity" data-shape="round" id="{elem.id}" cx="{cx}" cy="{cy}" r="{r}"{transform} />'
                )
            else:
                svg_lines.append(
                    f'  <rect class="tablet-cavity" data-shape="non-round" id="{elem.id}" x="{elem.x_mm}" y="{elem.y_mm}" '
                    f'width="{elem.width_mm}" height="{elem.height_mm}" rx="1" ry="1"{transform} />'
                )
        elif elem.type == ElementType.CODE:
            code_type_str = ""
            if elem.code_type:
                code_type_str = elem.code_type.value if hasattr(elem.code_type, "value") else str(elem.code_type)
            code_type_lower = code_type_str.lower()
            content_lower = (elem.content or "").lower()

            if "datamatrix" in code_type_lower or "datamatrix" in content_lower:
                label = f"[DataMatrix: {escaped_content}]" if escaped_content else "[DataMatrix Area]"
                svg_lines.append(
                    f'  <g id="{elem.id}" class="layout-code-group code-datamatrix"{transform}>'
                    f'    <rect class="layout-code code-reserved-datamatrix" x="{elem.x_mm}" y="{elem.y_mm}" '
                    f'width="{elem.width_mm}" height="{elem.height_mm}" rx="0.5" ry="0.5" />'
                    f'    <text class="layout-code-reserved-text" x="{cx}" y="{cy}" '
                    f'text-anchor="middle" dominant-baseline="central">{label}</text>'
                    f'  </g>'
                )
            elif "qr" in code_type_lower or "qr" in content_lower:
                label = f"[QR Code: {escaped_content}]" if escaped_content else "[QR Code Area]"
                svg_lines.append(
                    f'  <g id="{elem.id}" class="layout-code-group code-qr"{transform}>'
                    f'    <rect class="layout-code code-reserved-qr" x="{elem.x_mm}" y="{elem.y_mm}" '
                    f'width="{elem.width_mm}" height="{elem.height_mm}" rx="0.5" ry="0.5" />'
                    f'    <text class="layout-code-reserved-text" x="{cx}" y="{cy}" '
                    f'text-anchor="middle" dominant-baseline="central">{label}</text>'
                    f'  </g>'
                )
            elif "barcode" in code_type_lower or "barcode" in content_lower:
                label = f"[Barcode: {escaped_content}]" if escaped_content else "[Barcode Area]"
                svg_lines.append(
                    f'  <g id="{elem.id}" class="layout-code-group code-barcode"{transform}>'
                    f'    <rect class="layout-code code-reserved-barcode" x="{elem.x_mm}" y="{elem.y_mm}" '
                    f'width="{elem.width_mm}" height="{elem.height_mm}" rx="0.5" ry="0.5" />'
                    f'    <text class="layout-code-reserved-text" x="{cx}" y="{cy}" '
                    f'text-anchor="middle" dominant-baseline="central">{label}</text>'
                    f'  </g>'
                )
            else:  # human-readable code
                svg_lines.append(
                    f'  <g id="{elem.id}" class="layout-code-group code-human-readable"{transform}>'
                    f'    <rect class="layout-code" x="{elem.x_mm}" y="{elem.y_mm}" width="{elem.width_mm}" height="{elem.height_mm}" />'
                    f'    <text class="layout-code-text" x="{elem.x_mm + 0.5}" y="{elem.y_mm + 0.5}">{escaped_content}</text>'
                    f'  </g>'
                )
        elif elem.type == ElementType.TEXT:
            font_size = elem.font_size_mm or 2.5
            svg_lines.append(
                f'  <text class="layout-text" id="{elem.id}" x="{elem.x_mm}" y="{elem.y_mm}" '
                f'font-size="{font_size}mm"{transform}>{escaped_content}</text>'
            )
        else:  # RECTANGLE or others
            svg_lines.append(
                f'  <rect class="layout-rect" id="{elem.id}" x="{elem.x_mm}" y="{elem.y_mm}" '
                f'width="{elem.width_mm}" height="{elem.height_mm}"{transform} />'
            )

    svg_lines.append("</svg>")
    return "\n".join(svg_lines)
