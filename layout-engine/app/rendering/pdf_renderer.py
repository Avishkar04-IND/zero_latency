import math
from typing import List, Optional, Tuple

from app.models.layout_models import ElementType, LayoutPlan

# Conversion constant: 72 points per inch, 25.4 mm per inch
MM_TO_POINTS = 72.0 / 25.4


def _escape_pdf_string(text: str) -> str:
    """Escapes special characters in PDF literal text strings."""
    if not text:
        return ""
    # Map any non-ascii or problematic characters to safe representation
    out = []
    for ch in text:
        if ch == "\\":
            out.append("\\\\")
        elif ch == "(":
            out.append("\\(")
        elif ch == ")":
            out.append("\\)")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif 32 <= ord(ch) <= 126:
            out.append(ch)
        else:
            # Octal escape or fallback for standard WinAnsiEncoding
            out.append(f"\\{ord(ch):03o}")
    return "".join(out)


def _draw_circle_bezier(cx: float, cy: float, r: float) -> str:
    """Draws a circle using 4 cubic Bézier curve segments.
    Approximation constant k = r * 0.552284749831.
    """
    k = r * 0.552284749831
    lines = [
        f"{cx + r:.3f} {cy:.3f} m",
        f"{cx + r:.3f} {cy + k:.3f} {cx + k:.3f} {cy + r:.3f} {cx:.3f} {cy + r:.3f} c",
        f"{cx - k:.3f} {cy + r:.3f} {cx - r:.3f} {cy + k:.3f} {cx - r:.3f} {cy:.3f} c",
        f"{cx - r:.3f} {cy - k:.3f} {cx - k:.3f} {cy - r:.3f} {cx:.3f} {cy - r:.3f} c",
        f"{cx + k:.3f} {cy - r:.3f} {cx + r:.3f} {cy - k:.3f} {cx + r:.3f} {cy:.3f} c",
        "h",
    ]
    return " ".join(lines)


def render_layout_to_pdf(layout: LayoutPlan) -> bytes:
    """Renders an existing LayoutPlan to physical PDF bytes.

    Converts layout coordinates from millimeters to PDF points (points = mm * 72 / 25.4).
    Preserves exact physical dimensions and aspect ratio without altering or recalculating
    element placements.

    Renders:
      - Package boundary and printable area
      - Tablet cavities (round as circles, non-round as rectangles)
      - Medicine text elements (name, strength, ingredients, healthcare use, batch,
        MFG, EXP, manufacturer, MRP, storage, warnings)
      - Human-readable code
      - DataMatrix / Barcode reserved physical areas and labels
    """
    if layout is None:
        raise ValueError("Cannot render PDF: LayoutPlan is None.")
    if layout.package is None:
        raise ValueError("Cannot render PDF: LayoutPlan missing package information.")
    if not layout.success or (layout.validation is not None and not layout.validation.valid):
        errs = layout.errors or (layout.validation.errors if layout.validation else [])
        err_msg = "; ".join(errs) if errs else "Layout generation was unsuccessful"
        raise ValueError(f"Cannot render PDF: {err_msg}")

    pkg = layout.package
    w_mm = pkg.package_width_mm
    h_mm = pkg.package_height_mm

    if w_mm <= 0 or h_mm <= 0:
        raise ValueError(f"Cannot render PDF: Invalid package dimensions ({w_mm}x{h_mm}mm).")

    page_w_pt = w_mm * MM_TO_POINTS
    page_h_pt = h_mm * MM_TO_POINTS

    commands: List[str] = []

    # 1. Background / Package Boundary
    # Layout (0, 0) top-left -> PDF (0, 0) bottom-left
    commands.append("% --- Package Boundary ---")
    commands.append("q")
    commands.append("1 1 1 rg")  # White fill
    commands.append("0.12 0.16 0.23 RG")  # Slate border
    commands.append("0.75 w")
    commands.append(f"0 0 {page_w_pt:.3f} {page_h_pt:.3f} re B")
    commands.append("Q")

    # 2. Printable Area Boundary (dashed)
    commands.append("% --- Printable Area ---")
    commands.append("q")
    commands.append("0.97 0.98 0.99 rg")  # Very light background for printable zone
    commands.append("0.58 0.64 0.72 RG")  # Light slate stroke
    commands.append("[2 2] 0 d")  # Dashed line
    commands.append("0.5 w")
    pa_x_pt = pkg.printing_area_x_mm * MM_TO_POINTS
    pa_y_pt = (h_mm - (pkg.printing_area_y_mm + pkg.printing_area_height_mm)) * MM_TO_POINTS
    pa_w_pt = pkg.printing_area_width_mm * MM_TO_POINTS
    pa_h_pt = pkg.printing_area_height_mm * MM_TO_POINTS
    commands.append(f"{pa_x_pt:.3f} {pa_y_pt:.3f} {pa_w_pt:.3f} {pa_h_pt:.3f} re B")
    commands.append("Q")

    # 3. Layout Elements
    for elem in layout.elements:
        commands.append(f"% --- Element: {elem.id} ({elem.type.value if hasattr(elem.type, 'value') else elem.type}) ---")
        commands.append("q")

        # Element geometry in points
        elem_x_pt = elem.x_mm * MM_TO_POINTS
        elem_y_pt = (h_mm - (elem.y_mm + elem.height_mm)) * MM_TO_POINTS
        elem_w_pt = elem.width_mm * MM_TO_POINTS
        elem_h_pt = elem.height_mm * MM_TO_POINTS

        # Element center for rotation
        cx_pt = (elem.x_mm + elem.width_mm / 2.0) * MM_TO_POINTS
        cy_pt = (h_mm - (elem.y_mm + elem.height_mm / 2.0)) * MM_TO_POINTS

        # Apply rotation if present
        if elem.rotation_deg:
            # Layout rotation is clockwise; in Cartesian PDF space clockwise is negative angle
            rad = -math.radians(elem.rotation_deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            # Translation to center, rotate, translation back:
            # Matrix composition: [cos, sin, -sin, cos, cx*(1-cos) + cy*sin, cy*(1-cos) - cx*sin]
            e = cx_pt * (1.0 - cos_a) + cy_pt * sin_a
            f = cy_pt * (1.0 - cos_a) - cx_pt * sin_a
            commands.append(f"{cos_a:.6f} {sin_a:.6f} {-sin_a:.6f} {cos_a:.6f} {e:.3f} {f:.3f} cm")

        if elem.type == ElementType.TABLET_CAVITY:
            commands.append("0.88 0.91 0.94 rg")  # Soft slate fill
            commands.append("0.39 0.45 0.55 RG")  # Border stroke
            commands.append("0.5 w")
            # Determine if circular (round) or rectangular (non-round)
            if abs(elem.width_mm - elem.height_mm) < 1e-4:
                r_pt = elem_w_pt / 2.0
                circle_path = _draw_circle_bezier(cx_pt, cy_pt, r_pt)
                commands.append(f"{circle_path} B")
            else:
                commands.append(f"{elem_x_pt:.3f} {elem_y_pt:.3f} {elem_w_pt:.3f} {elem_h_pt:.3f} re B")

        elif elem.type == ElementType.CODE:
            code_type_str = ""
            if elem.code_type:
                code_type_str = elem.code_type.value if hasattr(elem.code_type, "value") else str(elem.code_type)
            code_type_lower = code_type_str.lower()
            content = elem.content or ""
            content_lower = content.lower()

            if "datamatrix" in code_type_lower or "datamatrix" in content_lower:
                # Reserved DataMatrix area
                commands.append("0.94 0.96 1.0 rg")  # Very light blue fill
                commands.append("0.15 0.39 0.92 RG")  # Blue border
                commands.append("[2 1] 0 d")  # Dashed pattern
                commands.append("0.5 w")
                commands.append(f"{elem_x_pt:.3f} {elem_y_pt:.3f} {elem_w_pt:.3f} {elem_h_pt:.3f} re B")
                # Label text
                label = f"[DataMatrix: {content}]" if content else "[DataMatrix Area]"
                label_escaped = _escape_pdf_string(label)
                font_size_pt = max(4.5, min(elem_h_pt * 0.35, 7.0))
                # Center label horizontally and vertically
                approx_text_width = len(label) * font_size_pt * 0.48
                tx = max(elem_x_pt + 1.0, cx_pt - approx_text_width / 2.0)
                ty = cy_pt - font_size_pt * 0.35
                commands.append("0.11 0.31 0.85 rg")  # Text color
                commands.append(f"BT /F2 {font_size_pt:.2f} Tf {tx:.2f} {ty:.2f} Td ({label_escaped}) Tj ET")

            elif "barcode" in code_type_lower or "barcode" in content_lower:
                # Reserved Barcode area
                commands.append("0.94 0.96 1.0 rg")
                commands.append("0.15 0.39 0.92 RG")
                commands.append("[3 1.5] 0 d")
                commands.append("0.5 w")
                commands.append(f"{elem_x_pt:.3f} {elem_y_pt:.3f} {elem_w_pt:.3f} {elem_h_pt:.3f} re B")
                label = f"[Barcode: {content}]" if content else "[Barcode Area]"
                label_escaped = _escape_pdf_string(label)
                font_size_pt = max(4.5, min(elem_h_pt * 0.35, 7.0))
                approx_text_width = len(label) * font_size_pt * 0.48
                tx = max(elem_x_pt + 1.0, cx_pt - approx_text_width / 2.0)
                ty = cy_pt - font_size_pt * 0.35
                commands.append("0.11 0.31 0.85 rg")
                commands.append(f"BT /F2 {font_size_pt:.2f} Tf {tx:.2f} {ty:.2f} Td ({label_escaped}) Tj ET")

            else:
                # Human-readable code
                commands.append("0.95 0.96 0.98 rg")  # Background tint
                commands.append("0.01 0.52 0.78 RG")  # Cyan/teal border
                commands.append("0.4 w")
                commands.append(f"{elem_x_pt:.3f} {elem_y_pt:.3f} {elem_w_pt:.3f} {elem_h_pt:.3f} re B")
                # Text inside code box
                text_content = _escape_pdf_string(content)
                font_size_pt = (elem.font_size_mm * MM_TO_POINTS) if elem.font_size_mm else max(5.0, elem_h_pt * 0.6)
                tx = elem_x_pt + 2.0
                ty = elem_y_pt + (elem_h_pt - font_size_pt) / 2.0
                commands.append("0.01 0.41 0.63 rg")
                commands.append(f"BT /F3 {font_size_pt:.2f} Tf {tx:.2f} {ty:.2f} Td ({text_content}) Tj ET")

        elif elem.type == ElementType.TEXT:
            # Physical selectable text element
            content = elem.content or ""
            text_escaped = _escape_pdf_string(content)
            font_size_mm = elem.font_size_mm or 2.5
            font_size_pt = font_size_mm * MM_TO_POINTS

            # Select font based on element id / importance
            elem_id_lower = elem.id.lower()
            if "name" in elem_id_lower or "title" in elem_id_lower:
                font_ref = "/F2"  # Helvetica-Bold
                commands.append("0.06 0.09 0.16 rg")  # Dark bold
            elif "warning" in elem_id_lower:
                font_ref = "/F2"  # Helvetica-Bold
                commands.append("0.75 0.10 0.10 rg")  # Dark red for warnings
            else:
                font_ref = "/F1"  # Helvetica Regular
                commands.append("0.10 0.14 0.20 rg")  # Standard dark text

            # Top-left of text element box: baseline offset is approx 0.75 * font_size
            tx = elem_x_pt
            ty = (h_mm - elem.y_mm) * MM_TO_POINTS - font_size_pt * 0.78
            commands.append(f"BT {font_ref} {font_size_pt:.2f} Tf {tx:.2f} {ty:.2f} Td ({text_escaped}) Tj ET")

        else:
            # Generic rectangle
            commands.append("0.80 0.83 0.88 RG")
            commands.append("0.3 w")
            commands.append(f"{elem_x_pt:.3f} {elem_y_pt:.3f} {elem_w_pt:.3f} {elem_h_pt:.3f} re S")

        commands.append("Q")

    content_stream = "\n".join(commands)
    content_bytes = content_stream.encode("latin-1", errors="replace")

    # Construct standard-compliant PDF 1.4 objects
    objects: List[Tuple[int, bytes]] = []

    # Object 1: Catalog
    catalog_body = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects.append((1, catalog_body))

    # Object 2: Pages
    pages_body = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    objects.append((2, pages_body))

    # Object 3: Page (MediaBox matches package dimensions in points)
    page_body = (
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w_pt:.3f} {page_h_pt:.3f}] "
        f"/Contents 4 0 R /Resources 5 0 R >>"
    ).encode("ascii")
    objects.append((3, page_body))

    # Object 4: Content Stream
    stream_header = f"<< /Length {len(content_bytes)} >>\nstream\n".encode("ascii")
    stream_footer = b"\nendstream"
    stream_body = stream_header + content_bytes + stream_footer
    objects.append((4, stream_body))

    # Object 5: Resources dictionary with fonts
    resources_body = (
        b"<< /ProcSet [/PDF /Text] "
        b"/Font << /F1 6 0 R /F2 7 0 R /F3 8 0 R >> >>"
    )
    objects.append((5, resources_body))

    # Object 6: Font Helvetica (Standard 14 Font)
    font_f1 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objects.append((6, font_f1))

    # Object 7: Font Helvetica-Bold
    font_f2 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"
    objects.append((7, font_f2))

    # Object 8: Font Courier (Monospace for codes)
    font_f3 = b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>"
    objects.append((8, font_f3))

    # Build binary PDF output with xref table and trailer
    pdf_out = bytearray()
    pdf_out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets: List[int] = [0] * (len(objects) + 1)
    for obj_id, obj_data in objects:
        offsets[obj_id] = len(pdf_out)
        pdf_out.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        pdf_out.extend(obj_data)
        pdf_out.extend(b"\nendobj\n")

    xref_offset = len(pdf_out)
    pdf_out.extend(b"xref\n")
    pdf_out.extend(f"0 {len(objects) + 1}\n".encode("ascii"))
    pdf_out.extend(b"0000000000 65535 f \n")
    for i in range(1, len(objects) + 1):
        pdf_out.extend(f"{offsets[i]:010d} 00000 n \n".encode("ascii"))

    pdf_out.extend(b"trailer\n")
    pdf_out.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii"))
    pdf_out.extend(b"startxref\n")
    pdf_out.extend(f"{xref_offset}\n".encode("ascii"))
    pdf_out.extend(b"%%EOF\n")

    return bytes(pdf_out)
