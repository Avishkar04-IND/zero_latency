import math
from typing import Dict, List, Optional, Tuple

from app.geometry.geometry import (
    Rect,
    calculate_tablet_marking_area,
    compute_bounding_box,
)
from app.models.layout_models import (
    ElementType,
    LayoutAlternative,
    LayoutElement,
    LayoutPlan,
    LayoutRequest,
    ValidationResult,
)
from app.optimizer.optimizer import validate_layout


def calculate_cost_efficiency(
    elements: List[LayoutElement],
    printable_area_w: float,
    printable_area_h: float,
) -> Tuple[float, float, float]:
    """Calculates explainable cost efficiency metrics for physical layout packaging.

    Formulas:
    - total_area = printable_area_w * printable_area_h (mm^2)
    - used_printable_area = bounding box area of printed non-cavity elements (mm^2)
    - unused_printable_area = max(0, total_area - used_printable_area) (mm^2)
    - packing_density = sum(element_area) / max(1, used_printable_area)
    - footprint_compactness = 1.0 - (used_printable_area / total_area)
    - cost_efficiency = round(0.6 * packing_density + 0.4 * footprint_compactness, 4)
    """
    total_area = max(1.0, printable_area_w * printable_area_h)

    printed_elems = [e for e in elements if e.type != ElementType.TABLET_CAVITY]
    if not printed_elems:
        printed_elems = elements

    if not printed_elems:
        return 0.0, 0.0, total_area

    rects = [Rect(e.x_mm, e.y_mm, e.width_mm, e.height_mm) for e in printed_elems]
    bbox = compute_bounding_box(rects)
    used_area = round(bbox.area, 2)
    unused_area = round(max(0.0, total_area - used_area), 2)

    total_elem_area = sum(r.area for r in rects)
    packing_density = min(1.0, total_elem_area / max(1.0, bbox.area))
    compactness = max(0.0, 1.0 - min(1.0, bbox.area / total_area))

    cost_eff = round(0.6 * packing_density + 0.4 * compactness, 4)
    return cost_eff, used_area, unused_area


def calculate_balanced_score(
    elements: List[LayoutElement],
    printable_area_w: float,
    printable_area_h: float,
) -> Tuple[float, float, float, float, float]:
    """Calculates explainable balanced metrics [0.0, 1.0] representing trade-offs between

    space utilization, readability, print efficiency, and code reliability.

    Formula:
      balanced_score = (
          0.30 * space_utilization
        + 0.25 * readability
        + 0.25 * print_efficiency
        + 0.20 * code_reliability
      )
    """
    total_area = max(1.0, printable_area_w * printable_area_h)
    if not elements:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    rects = [Rect(e.x_mm, e.y_mm, e.width_mm, e.height_mm) for e in elements]
    bbox = compute_bounding_box(rects)
    total_elem_area = sum(r.area for r in rects)

    # 1. space_utilization [0.0, 1.0]: element density within bounding footprint
    space_utilization = round(min(1.0, total_elem_area / max(1.0, bbox.area)), 4)

    # 2. readability [0.0, 1.0]: text font scale and element spacing clearance
    text_elems = [e for e in elements if e.type == ElementType.TEXT]
    if text_elems:
        avg_font = sum(e.font_size_mm or 2.5 for e in text_elems) / len(text_elems)
        font_score = min(1.0, avg_font / 3.0)
    else:
        font_score = 0.8

    if len(elements) > 1:
        min_dists = []
        for i, r1 in enumerate(rects):
            d = min(r1.distance_to(rects[j]) for j in range(len(rects)) if i != j)
            min_dists.append(d)
        avg_dist = sum(min_dists) / len(min_dists)
        spacing_score = min(1.0, max(0.2, avg_dist / 2.0))
    else:
        spacing_score = 1.0

    readability = round(0.5 * font_score + 0.5 * spacing_score, 4)

    # 3. print_efficiency [0.0, 1.0]: balanced coverage (avoids extreme crowding or extreme dispersion)
    footprint_ratio = bbox.area / total_area
    if footprint_ratio <= 0.85:
        print_efficiency = round(min(1.0, 0.5 + 0.5 * (1.0 - footprint_ratio / 0.85)), 4)
    else:
        print_efficiency = round(max(0.2, 0.5 * (1.0 - (footprint_ratio - 0.85) / 0.15)), 4)

    # 4. code_reliability [0.0, 1.0]: code orientation and quiet zone clearance
    code_elems = [e for e in elements if e.type == ElementType.CODE]
    if code_elems:
        code_e = code_elems[0]
        code_r = Rect(code_e.x_mm, code_e.y_mm, code_e.width_mm, code_e.height_mm)
        rot_score = 1.0 if code_e.rotation_deg in (0.0, 180.0) else 0.85
        other_rects = [r for idx, r in enumerate(rects) if elements[idx].id != code_e.id]
        if other_rects:
            min_code_dist = min(code_r.distance_to(r) for r in other_rects)
            quiet_zone_score = min(1.0, max(0.3, min_code_dist / 1.5))
        else:
            quiet_zone_score = 1.0
        code_reliability = round(0.5 * rot_score + 0.5 * quiet_zone_score, 4)
    else:
        code_reliability = 1.0

    balanced_score = round(
        0.30 * space_utilization
        + 0.25 * readability
        + 0.25 * print_efficiency
        + 0.20 * code_reliability,
        4,
    )
    return balanced_score, space_utilization, readability, print_efficiency, code_reliability


def calculate_accessibility_score(
    elements: List[LayoutElement],
    printable_area_w: float,
    printable_area_h: float,
) -> Tuple[float, float, float, float, float]:
    """Calculates explainable accessibility metrics [0.0, 1.0] prioritizing readability,
    spacing quality, whitespace quality, and code reliability.

    Formula:
      accessibility_score = (
          0.35 * readability
        + 0.25 * spacing_quality
        + 0.20 * whitespace_quality
        + 0.20 * code_reliability
      )
    """
    total_area = max(1.0, printable_area_w * printable_area_h)
    if not elements:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    rects = [Rect(e.x_mm, e.y_mm, e.width_mm, e.height_mm) for e in elements]
    bbox = compute_bounding_box(rects)
    total_elem_area = sum(r.area for r in rects)

    # 1. readability [0.0, 1.0]: text font scale and text bounding box scale
    text_elems = [e for e in elements if e.type == ElementType.TEXT]
    if text_elems:
        avg_font = sum(e.font_size_mm or 2.5 for e in text_elems) / len(text_elems)
        font_score = min(1.0, avg_font / 3.2)
        avg_h = sum(e.height_mm for e in text_elems) / len(text_elems)
        box_score = min(1.0, avg_h / 4.0)
        readability = round(0.6 * font_score + 0.4 * box_score, 4)
    else:
        readability = 1.0

    # 2. spacing_quality [0.0, 1.0]: distance between all pairwise elements
    if len(elements) > 1:
        min_dists = []
        for i, r1 in enumerate(rects):
            d = min(r1.distance_to(rects[j]) for j in range(len(rects)) if i != j)
            min_dists.append(d)
        avg_dist = sum(min_dists) / len(min_dists)
        spacing_quality = round(min(1.0, max(0.0, avg_dist / 2.5)), 4)
    else:
        spacing_quality = 1.0

    # 3. whitespace_quality [0.0, 1.0]: avoidance of overcrowding, proportion of clean whitespace
    coverage = total_elem_area / total_area
    whitespace_ratio = max(0.0, 1.0 - coverage)
    whitespace_quality = round(min(1.0, max(0.1, whitespace_ratio)), 4)

    # 4. code_reliability [0.0, 1.0]: code orientation and quiet zone clearance
    code_elems = [e for e in elements if e.type == ElementType.CODE]
    if code_elems:
        code_e = code_elems[0]
        code_r = Rect(code_e.x_mm, code_e.y_mm, code_e.width_mm, code_e.height_mm)
        rot_score = 1.0 if code_e.rotation_deg in (0.0, 180.0) else 0.85
        other_rects = [r for idx, r in enumerate(rects) if elements[idx].id != code_e.id]
        if other_rects:
            min_code_dist = min(code_r.distance_to(r) for r in other_rects)
            quiet_zone_score = min(1.0, max(0.2, min_code_dist / 2.0))
        else:
            quiet_zone_score = 1.0
        code_reliability = round(0.5 * rot_score + 0.5 * quiet_zone_score, 4)
    else:
        code_reliability = 1.0

    accessibility_score = round(
        0.35 * readability
        + 0.25 * spacing_quality
        + 0.20 * whitespace_quality
        + 0.20 * code_reliability,
        4,
    )
    return accessibility_score, readability, spacing_quality, whitespace_quality, code_reliability


def calculate_common_score(
    scan_reliability: float,
    space_utilization: float,
    readability: float,
    print_efficiency: float,
    cost_efficiency: float,
) -> float:
    """Calculates the exact common recommendation score from 0.0 to 1.0:
      score = (
          0.30 * scan_reliability
        + 0.25 * space_utilization
        + 0.20 * readability
        + 0.15 * print_efficiency
        + 0.10 * cost_efficiency
      )
    """
    raw_score = (
        0.30 * scan_reliability
        + 0.25 * space_utilization
        + 0.20 * readability
        + 0.15 * print_efficiency
        + 0.10 * cost_efficiency
    )
    return round(max(0.0, min(1.0, raw_score)), 4)


def _generate_candidate(
    request: LayoutRequest,
    strategy: str = "compact_tl",
) -> LayoutPlan:
    """Generates a single deterministic layout candidate under a specified packing strategy."""
    pkg = request.package
    min_margin = request.min_margin_mm if request.min_margin_mm is not None else request.constraints.minimum_margin_mm
    spacing = request.constraints.minimum_element_spacing_mm

    # Add spacing buffer for spacious/accessibility strategies
    if strategy in ("accessibility_spacious", "code_clearance"):
        spacing = max(spacing, 2.0)
    elif strategy in ("balanced_spacious", "critical_info_priority", "readable_columns", "readable_rows"):
        spacing = max(spacing, 1.8)

    is_accessibility = strategy in (
        "accessibility_spacious",
        "critical_info_priority",
        "code_clearance",
        "readable_columns",
        "readable_rows",
    )

    pkg_rect = Rect(0.0, 0.0, pkg.package_width_mm, pkg.package_height_mm)
    print_rect = Rect(
        pkg.printing_area_x_mm,
        pkg.printing_area_y_mm,
        pkg.printing_area_width_mm,
        pkg.printing_area_height_mm,
    )

    usable_x = pkg.printing_area_x_mm + min_margin
    usable_y = pkg.printing_area_y_mm + min_margin
    usable_w = pkg.printing_area_width_mm - 2.0 * min_margin
    usable_h = pkg.printing_area_height_mm - 2.0 * min_margin

    if usable_w <= 0.0 or usable_h <= 0.0:
        msg = f"No valid placement found: insufficient printable area ({pkg.printing_area_width_mm}x{pkg.printing_area_height_mm}mm) for minimum {min_margin}mm margin."
        return LayoutPlan(
            id="layout_failed",
            package=pkg,
            elements=[],
            success=False,
            errors=[msg],
            validation=ValidationResult(valid=False, errors=[msg]),
        )

    placed_elements: List[LayoutElement] = []
    occupied_rects: List[Rect] = []

    # 1. Tablet Cavities Placement
    t_count = request.tablet.tablet_count
    t_w = request.tablet.effective_width_mm
    t_h = request.tablet.effective_height_mm

    if request.tablet.positions:
        for idx, pos in enumerate(request.tablet.positions):
            cw = pos.width_mm or t_w
            ch = pos.height_mm or t_h
            cid = pos.id or f"cavity_{idx + 1}"
            crect = Rect(pos.x_mm, pos.y_mm, cw, ch)

            if not pkg_rect.contains(crect):
                msg = f"Supplied tablet cavity '{cid}' crosses package boundary."
                return LayoutPlan(id="layout_failed", package=pkg, elements=[], success=False, errors=[msg], validation=ValidationResult(valid=False, errors=[msg]))

            for prev_r in occupied_rects:
                if crect.intersects(prev_r):
                    msg = f"Supplied tablet cavity '{cid}' overlaps another cavity."
                    return LayoutPlan(id="layout_failed", package=pkg, elements=[], success=False, errors=[msg], validation=ValidationResult(valid=False, errors=[msg]))

            elem = LayoutElement(id=cid, type=ElementType.TABLET_CAVITY, x_mm=pos.x_mm, y_mm=pos.y_mm, width_mm=cw, height_mm=ch)
            placed_elements.append(elem)
            occupied_rects.append(crect)
    else:
        cavity_spacing = max(spacing, 2.0)
        valid_grids = []

        for cols in range(1, t_count + 1):
            rows = math.ceil(t_count / cols)
            grid_w = cols * t_w + (cols - 1) * cavity_spacing
            grid_h = rows * t_h + (rows - 1) * cavity_spacing
            if grid_w + 2 * min_margin <= pkg.package_width_mm and grid_h + 2 * min_margin <= pkg.package_height_mm:
                ar_diff = abs((grid_w / grid_h) - (pkg.package_width_mm / pkg.package_height_mm))
                valid_grids.append((ar_diff, cols, rows, grid_w, grid_h))

        if not valid_grids:
            msg = f"Impossible tablet arrangement: package dimensions ({pkg.package_width_mm}x{pkg.package_height_mm}mm) cannot contain {t_count} tablets ({t_w}x{t_h}mm)."
            return LayoutPlan(id="layout_failed", package=pkg, elements=[], success=False, errors=[msg], validation=ValidationResult(valid=False, errors=[msg]))

        if strategy == "cavity_alt" and len(valid_grids) > 1:
            valid_grids.sort(key=lambda g: (-g[0], g[1]))
        else:
            valid_grids.sort(key=lambda g: (g[0], g[2]))

        _, best_cols, best_rows, grid_w, grid_h = valid_grids[0]

        if strategy == "cavity_top":
            start_x = (pkg.package_width_mm - grid_w) / 2.0
            start_y = min_margin
        elif pkg.package_height_mm >= pkg.package_width_mm:
            start_x = (pkg.package_width_mm - grid_w) / 2.0
            start_y = pkg.package_height_mm - grid_h - min_margin
        else:
            start_x = pkg.package_width_mm - grid_w - min_margin
            start_y = (pkg.package_height_mm - grid_h) / 2.0

        for i in range(t_count):
            c = i % best_cols
            r = i // best_cols
            cx = start_x + c * (t_w + cavity_spacing)
            cy = start_y + r * (t_h + cavity_spacing)
            cid = f"cavity_{i + 1}"
            elem = LayoutElement(id=cid, type=ElementType.TABLET_CAVITY, x_mm=cx, y_mm=cy, width_mm=t_w, height_mm=t_h)
            placed_elements.append(elem)
            occupied_rects.append(Rect(cx, cy, t_w, t_h))

    # 2. Tablet Marking Check
    warnings: List[str] = []
    if request.marking and request.marking.marking_enabled:
        marking_area = calculate_tablet_marking_area(t_w, t_h, is_round=(request.tablet.tablet_diameter_mm is not None))
        if request.marking.code_value:
            if len(request.marking.code_value) * 1.5 > marking_area.width:
                warnings.append(f"Tablet marking code '{request.marking.code_value}' exceeds recommended marking area.")

    # 3. Collect Items to Place
    items_to_place = []
    info = request.information
    if info:
        if info.medicine_name:
            if is_accessibility:
                w = min(usable_w, max(24.0, len(info.medicine_name) * 2.3))
                h = 4.8
                f_size = max(request.constraints.minimum_text_size_mm or 3.2, 3.2)
            else:
                w = min(usable_w, max(22.0, len(info.medicine_name) * 2.2))
                h = 4.5
                f_size = max(request.constraints.minimum_text_size_mm or 3.0, 3.0)
            items_to_place.append(("med_name", ElementType.TEXT, info.medicine_name, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.strength:
            if is_accessibility:
                w = min(usable_w, max(16.0, len(info.strength) * 2.1))
                h = 4.2
                f_size = max(request.constraints.minimum_text_size_mm or 2.8, 2.8)
            else:
                w = min(usable_w, max(14.0, len(info.strength) * 2.0))
                h = 4.0
                f_size = max(request.constraints.minimum_text_size_mm or 2.5, 2.5)
            items_to_place.append(("med_strength", ElementType.TEXT, info.strength, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.batch:
            text = f"B.No: {info.batch}"
            w = min(usable_w, max(16.0, len(text) * 1.8))
            h = 3.2
            f_size = max(request.constraints.minimum_text_size_mm or 2.0, 2.0)
            items_to_place.append(("batch_no", ElementType.TEXT, text, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.mfg:
            text = f"MFG: {info.mfg}"
            w = min(usable_w, max(16.0, len(text) * 1.8))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("mfg_date", ElementType.TEXT, text, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.exp:
            text = f"EXP: {info.exp}"
            w = min(usable_w, max(16.0, len(text) * 1.8))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("exp_date", ElementType.TEXT, text, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.ingredients:
            text = f"Ing: {info.ingredients}"
            w = min(usable_w, max(20.0, len(text) * 1.6))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("ingredients", ElementType.TEXT, text, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.healthcare_use:
            w = min(usable_w, max(18.0, len(info.healthcare_use) * 1.5))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("healthcare_use", ElementType.TEXT, info.healthcare_use, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.manufacturer:
            text = f"Mfd: {info.manufacturer}"
            w = min(usable_w, max(18.0, len(text) * 1.6))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("manufacturer", ElementType.TEXT, text, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.mrp:
            text = f"MRP: {info.mrp}"
            w = min(usable_w, max(15.0, len(text) * 1.8))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("mrp", ElementType.TEXT, text, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.storage:
            w = min(usable_w, max(18.0, len(info.storage) * 1.5))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("storage", ElementType.TEXT, info.storage, w, h, f_size, [0.0, 90.0, 270.0]))
        if info.warnings:
            w = min(usable_w, max(20.0, len(info.warnings) * 1.5))
            h = 3.0
            f_size = max(request.constraints.minimum_text_size_mm or 1.8, 1.8)
            items_to_place.append(("warnings", ElementType.TEXT, info.warnings, w, h, f_size, [0.0, 90.0, 270.0]))

    if request.code:
        cval = request.code.code_value or request.code.value or "MED001"
        cw = request.code.code_width_mm or request.code.minimum_code_size_mm or 20.0
        ch = request.code.code_height_mm or 6.0
        rotations = [request.code.orientation_deg]
        for r in [0.0, 90.0, 270.0, 180.0]:
            if r not in rotations:
                rotations.append(r)
        items_to_place.append(("batch_code", ElementType.CODE, cval, cw, ch, None, rotations))

    if strategy in ("code_priority", "code_clearance"):
        code_items = [item for item in items_to_place if item[1] == ElementType.CODE]
        other_items = [item for item in items_to_place if item[1] != ElementType.CODE]
        items_to_place = code_items + other_items
    elif strategy in ("critical_info_priority", "accessibility_spacious"):
        critical_ids = ("med_name", "med_strength", "batch_no", "mfg_date", "exp_date", "batch_code", "warnings")
        crit_items = [item for item in items_to_place if item[0] in critical_ids]
        sec_items = [item for item in items_to_place if item[0] not in critical_ids]
        crit_sorted = []
        for cid in critical_ids:
            for item in crit_items:
                if item[0] == cid and item not in crit_sorted:
                    crit_sorted.append(item)
        items_to_place = crit_sorted + sec_items

    # Deterministic Placement Function
    def find_placement(elem_id: str, item_w: float, item_h: float, rotations: List[float]) -> Optional[Tuple[float, float, float, float, float]]:
        for rot in rotations:
            ew, eh = (item_h, item_w) if rot in (90.0, 270.0) else (item_w, item_h)
            if ew > usable_w or eh > usable_h:
                continue

            max_x = usable_x + usable_w - ew
            max_y = usable_y + usable_h - eh

            candidates = []
            if strategy == "compact_br":
                for p in placed_elements:
                    if p.type != ElementType.TABLET_CAVITY:
                        candidates.append((p.x_mm - ew - spacing, p.y_mm))
                        candidates.append((p.x_mm, p.y_mm - eh - spacing))
                candidates.extend([(max_x, max_y), (max_x, usable_y), (usable_x, max_y)])
            elif strategy in ("compact_row", "readable_rows"):
                for p in placed_elements:
                    if p.type != ElementType.TABLET_CAVITY:
                        candidates.append((p.x_mm + p.width_mm + spacing, p.y_mm))
                        candidates.append((usable_x, p.y_mm + p.height_mm + spacing))
                candidates.extend([(usable_x, usable_y), (max_x, usable_y)])
            elif strategy == "readable_columns":
                for p in placed_elements:
                    if p.type != ElementType.TABLET_CAVITY:
                        candidates.append((p.x_mm, p.y_mm + p.height_mm + spacing))
                        candidates.append((p.x_mm + p.width_mm + spacing, usable_y))
                candidates.extend([(usable_x, usable_y), (usable_x + (max_x - usable_x) / 2.0, usable_y)])
            elif strategy in ("accessibility_spacious", "balanced_spacious", "critical_info_priority", "code_clearance"):
                for p in placed_elements:
                    if p.type != ElementType.TABLET_CAVITY:
                        candidates.append((p.x_mm, p.y_mm + p.height_mm + spacing))
                        candidates.append((p.x_mm + p.width_mm + spacing, p.y_mm))
                candidates.extend([
                    (usable_x, usable_y),
                    (max_x, usable_y),
                    (usable_x, max_y),
                    (usable_x + (max_x - usable_x) / 2.0, usable_y),
                ])
            else:  # compact_tl / default
                for p in placed_elements:
                    if p.type != ElementType.TABLET_CAVITY:
                        candidates.append((p.x_mm, p.y_mm + p.height_mm + spacing))
                        candidates.append((p.x_mm + p.width_mm + spacing, p.y_mm))
                candidates.extend([
                    (usable_x, usable_y),
                    (usable_x, max_y),
                    (usable_x + (max_x - usable_x) / 2.0, usable_y),
                    (max_x, usable_y),
                ])

            step_y = max(1.0, min(3.0, eh / 2.0))
            step_x = max(1.0, min(5.0, ew / 2.0))
            curr_y = usable_y
            while curr_y <= max_y + 1e-4:
                curr_x = usable_x
                while curr_x <= max_x + 1e-4:
                    candidates.append((curr_x, curr_y))
                    curr_x += step_x
                curr_y += step_y

            for cx, cy in candidates:
                if cx < usable_x - 1e-4 or cx > max_x + 1e-4 or cy < usable_y - 1e-4 or cy > max_y + 1e-4:
                    continue

                cand_rect = Rect(cx, cy, ew, eh)
                if not print_rect.has_min_margin(cand_rect, min_margin):
                    continue

                collides = False
                for occ in occupied_rects:
                    if cand_rect.intersects(occ):
                        collides = True
                        break
                    if spacing > 0.0 and cand_rect.distance_to(occ) < spacing:
                        collides = True
                        break

                if not collides:
                    return cx, cy, ew, eh, rot

        return None

    for item_id, elem_type, content, iw, ih, font_size, rots in items_to_place:
        placement = find_placement(item_id, iw, ih, rots)
        if placement is None:
            msg = f"No valid placement found: insufficient printable area for required element '{item_id}' ({iw}x{ih}mm)."
            return LayoutPlan(
                id="layout_failed",
                package=pkg,
                elements=[],
                success=False,
                errors=[msg],
                validation=ValidationResult(valid=False, errors=[msg]),
            )

        cx, cy, ew, eh, rot = placement
        elem = LayoutElement(
            id=item_id,
            type=elem_type,
            content=content,
            x_mm=cx,
            y_mm=cy,
            width_mm=ew,
            height_mm=eh,
            font_size_mm=font_size,
            rotation_deg=rot,
            code_type=request.code.code_type if (elem_type == ElementType.CODE and request.code) else None,
        )
        placed_elements.append(elem)
        occupied_rects.append(Rect(cx, cy, ew, eh))

    plan = LayoutPlan(
        id=f"layout_candidate_{strategy}",
        package=pkg,
        elements=placed_elements,
        success=True,
        warnings=warnings,
    )
    plan.validation = validate_layout(plan, min_margin_mm=min_margin, min_spacing_mm=spacing)
    if not plan.validation.valid:
        plan.success = False
        plan.errors = plan.validation.errors

    return plan


def generate_cost_optimized_layout(request: LayoutRequest) -> LayoutPlan:
    """Evaluates multiple deterministic candidate placement strategies and selects the highest cost-efficiency valid layout."""
    pkg = request.package

    strategies = [
        "compact_tl",
        "compact_row",
        "compact_br",
        "code_priority",
        "cavity_alt",
    ]

    valid_candidates: List[Tuple[float, LayoutPlan]] = []
    evaluated_count = 0
    last_failure: Optional[LayoutPlan] = None

    for strat in strategies:
        candidate = _generate_candidate(request, strategy=strat)
        evaluated_count += 1

        if candidate.success and candidate.validation and candidate.validation.valid:
            cost_eff, used_area, unused_area = calculate_cost_efficiency(
                candidate.elements,
                pkg.printing_area_width_mm,
                pkg.printing_area_height_mm,
            )
            candidate.cost_efficiency = cost_eff
            candidate.used_printable_area = used_area
            candidate.unused_printable_area = unused_area
            candidate.optimization_strategy = strat
            candidate.sync_layout_dict()
            valid_candidates.append((cost_eff, candidate))
        else:
            last_failure = candidate

    if not valid_candidates:
        if last_failure is not None:
            last_failure.candidates_evaluated = evaluated_count
            return last_failure

        msg = "No valid placement found: insufficient printable area or geometry conflict."
        return LayoutPlan(
            id="layout_failed",
            package=pkg,
            elements=[],
            success=False,
            errors=[msg],
            candidates_evaluated=evaluated_count,
            validation=ValidationResult(valid=False, errors=[msg]),
        )

    valid_candidates.sort(key=lambda item: item[0], reverse=True)
    best_eff, best_plan = valid_candidates[0]

    best_plan.id = "layout_cost_optimized_001"
    best_plan.recommended_strategy = "COST"
    best_plan.recommended_layout = best_plan.layout
    best_plan.candidates_evaluated = evaluated_count
    best_plan.sync_layout_dict()
    return best_plan


def generate_balanced_layout(request: LayoutRequest) -> LayoutPlan:
    """Evaluates multiple deterministic candidate placement strategies and selects the highest balanced-score valid layout."""
    pkg = request.package

    strategies = [
        "balanced_spacious",
        "compact_row",
        "compact_tl",
        "code_priority",
        "cavity_alt",
    ]

    valid_candidates: List[Tuple[float, LayoutPlan]] = []
    evaluated_count = 0
    last_failure: Optional[LayoutPlan] = None

    for strat in strategies:
        candidate = _generate_candidate(request, strategy=strat)
        evaluated_count += 1

        if candidate.success and candidate.validation and candidate.validation.valid:
            b_score, space_u, read_s, print_e, code_r = calculate_balanced_score(
                candidate.elements,
                pkg.printing_area_width_mm,
                pkg.printing_area_height_mm,
            )
            cost_eff, used_area, unused_area = calculate_cost_efficiency(
                candidate.elements,
                pkg.printing_area_width_mm,
                pkg.printing_area_height_mm,
            )
            candidate.balanced_score = b_score
            candidate.space_utilization = space_u
            candidate.readability = read_s
            candidate.print_efficiency = print_e
            candidate.code_reliability = code_r
            candidate.cost_efficiency = cost_eff
            candidate.used_printable_area = used_area
            candidate.unused_printable_area = unused_area
            candidate.optimization_strategy = strat
            candidate.sync_layout_dict()
            valid_candidates.append((b_score, candidate))
        else:
            last_failure = candidate

    if not valid_candidates:
        if last_failure is not None:
            last_failure.candidates_evaluated = evaluated_count
            return last_failure

        msg = "No valid placement found: insufficient printable area or geometry conflict."
        return LayoutPlan(
            id="layout_failed",
            package=pkg,
            elements=[],
            success=False,
            errors=[msg],
            candidates_evaluated=evaluated_count,
            validation=ValidationResult(valid=False, errors=[msg]),
        )

    valid_candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, best_plan = valid_candidates[0]

    best_plan.id = "layout_balanced_optimized_001"
    best_plan.recommended_strategy = "BALANCED"
    best_plan.recommended_layout = best_plan.layout
    best_plan.candidates_evaluated = evaluated_count
    best_plan.sync_layout_dict()
    return best_plan


def generate_accessibility_layout(request: LayoutRequest) -> LayoutPlan:
    """Evaluates multiple deterministic candidate placement strategies and selects the highest accessibility-score valid layout."""
    pkg = request.package

    strategies = [
        "accessibility_spacious",
        "critical_info_priority",
        "code_clearance",
        "readable_columns",
        "readable_rows",
    ]

    valid_candidates: List[Tuple[float, LayoutPlan]] = []
    evaluated_count = 0
    last_failure: Optional[LayoutPlan] = None

    for strat in strategies:
        candidate = _generate_candidate(request, strategy=strat)
        evaluated_count += 1

        if candidate.success and candidate.validation and candidate.validation.valid:
            acc_score, read_s, space_q, white_q, code_r = calculate_accessibility_score(
                candidate.elements,
                pkg.printing_area_width_mm,
                pkg.printing_area_height_mm,
            )
            candidate.accessibility_score = acc_score
            candidate.readability = read_s
            candidate.spacing_quality = space_q
            candidate.whitespace_quality = white_q
            candidate.code_reliability = code_r
            candidate.optimization_strategy = strat
            candidate.sync_layout_dict()
            valid_candidates.append((acc_score, candidate))
        else:
            last_failure = candidate

    if not valid_candidates:
        if last_failure is not None:
            last_failure.candidates_evaluated = evaluated_count
            return last_failure

        msg = "No valid placement found: insufficient printable area or geometry conflict."
        return LayoutPlan(
            id="layout_failed",
            package=pkg,
            elements=[],
            success=False,
            errors=[msg],
            candidates_evaluated=evaluated_count,
            validation=ValidationResult(valid=False, errors=[msg]),
        )

    valid_candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, best_plan = valid_candidates[0]

    best_plan.id = "layout_accessibility_optimized_001"
    best_plan.recommended_strategy = "ACCESSIBILITY"
    best_plan.recommended_layout = best_plan.layout
    best_plan.candidates_evaluated = evaluated_count
    best_plan.sync_layout_dict()
    return best_plan


def generate_recommendation(request: LayoutRequest) -> LayoutPlan:
    """Evaluates Cost, Balanced, and Accessibility layouts under a common scoring model,
    applies deterministic tie-breaking, and returns the recommended layout along with all
    valid alternatives.
    """
    pkg = request.package
    strategy_priority = {"COST": 3, "BALANCED": 2, "ACCESSIBILITY": 1}
    strategies = ["COST", "BALANCED", "ACCESSIBILITY"]

    valid_alternatives: List[LayoutAlternative] = []
    valid_plans: Dict[str, LayoutPlan] = {}
    failed_strategies: List[str] = []
    all_errors: List[str] = []
    all_warnings: List[str] = []

    for strat in strategies:
        req_copy = request.model_copy(deep=True)
        req_copy.optimization_target = strat
        if strat == "COST":
            plan = generate_cost_optimized_layout(req_copy)
        elif strat == "BALANCED":
            plan = generate_balanced_layout(req_copy)
        elif strat == "ACCESSIBILITY":
            plan = generate_accessibility_layout(req_copy)
        else:
            continue

        if plan.success and plan.validation and plan.validation.valid:
            cost_e = plan.cost_efficiency
            if cost_e is None:
                cost_e, _, _ = calculate_cost_efficiency(
                    plan.elements, pkg.printing_area_width_mm, pkg.printing_area_height_mm
                )
                plan.cost_efficiency = cost_e

            space_u = plan.space_utilization
            read_s = plan.readability
            print_e = plan.print_efficiency
            scan_r = plan.code_reliability

            if any(m is None for m in (space_u, read_s, print_e, scan_r)):
                _, b_space, b_read, b_print, b_code = calculate_balanced_score(
                    plan.elements, pkg.printing_area_width_mm, pkg.printing_area_height_mm
                )
                if space_u is None:
                    space_u = b_space
                    plan.space_utilization = space_u
                if read_s is None:
                    read_s = b_read
                    plan.readability = read_s
                if print_e is None:
                    print_e = b_print
                    plan.print_efficiency = print_e
                if scan_r is None:
                    scan_r = b_code
                    plan.code_reliability = scan_r

            scan_r = scan_r if scan_r is not None else 1.0
            space_u = space_u if space_u is not None else 0.0
            read_s = read_s if read_s is not None else 0.0
            print_e = print_e if print_e is not None else 0.0
            cost_e = cost_e if cost_e is not None else 0.0

            comm_score = calculate_common_score(scan_r, space_u, read_s, print_e, cost_e)

            plan.score = comm_score
            plan.scan_reliability = scan_r
            plan.space_utilization = space_u
            plan.readability = read_s
            plan.print_efficiency = print_e
            plan.cost_efficiency = cost_e
            plan.sync_layout_dict()

            alt = LayoutAlternative(
                strategy=strat,
                layout=plan.layout,
                score=comm_score,
                space_utilization=space_u,
                readability=read_s,
                print_efficiency=print_e,
                cost_efficiency=cost_e,
                scan_reliability=scan_r,
                warnings=plan.warnings,
                errors=[],
            )
            valid_alternatives.append(alt)
            valid_plans[strat] = plan
        else:
            failed_strategies.append(strat)
            err_msg = f"Strategy '{strat}' failed: " + "; ".join(plan.errors or ["invalid geometry"])
            all_errors.append(err_msg)
            if plan.warnings:
                all_warnings.extend(plan.warnings)

    # All three strategies failed
    if not valid_alternatives:
        msg = "All layout strategies failed to produce a valid layout."
        return LayoutPlan(
            id="layout_recommendation_failed",
            package=pkg,
            elements=[],
            success=False,
            errors=[msg] + all_errors,
            warnings=all_warnings,
            recommended_strategy=None,
            recommended_layout=None,
            alternatives=[],
            validation=ValidationResult(valid=False, errors=[msg] + all_errors),
        )

    # Sort valid alternatives with deterministic tie-breaking
    valid_alternatives.sort(
        key=lambda a: (
            round(a.score, 4),
            round(a.scan_reliability, 4),
            round(a.readability, 4),
            round(a.space_utilization, 4),
            round(a.cost_efficiency, 4),
            strategy_priority.get(a.strategy, 0),
        ),
        reverse=True,
    )

    best_alt = valid_alternatives[0]
    best_strategy = best_alt.strategy
    best_plan = valid_plans[best_strategy]

    best_plan.id = f"layout_recommendation_{best_strategy.lower()}_001"
    best_plan.recommended_strategy = best_strategy
    best_plan.recommended_layout = best_alt.layout
    best_plan.alternatives = valid_alternatives
    best_plan.score = best_alt.score
    best_plan.scan_reliability = best_alt.scan_reliability
    best_plan.space_utilization = best_alt.space_utilization
    best_plan.readability = best_alt.readability
    best_plan.print_efficiency = best_alt.print_efficiency
    best_plan.cost_efficiency = best_alt.cost_efficiency

    if failed_strategies:
        best_plan.warnings.append(
            f"Note: strategies failed and excluded: {', '.join(failed_strategies)}"
        )

    best_plan.sync_layout_dict()
    return best_plan


def generate_layout(request: LayoutRequest) -> LayoutPlan:
    """Main placement entrypoint. Respects request.optimization_target (RECOMMEND, ACCESSIBILITY, BALANCED, COST)."""
    target = (request.optimization_target or "RECOMMEND").strip().upper()
    if target == "COST":
        return generate_cost_optimized_layout(request)
    elif target == "BALANCED":
        return generate_balanced_layout(request)
    elif target == "ACCESSIBILITY":
        return generate_accessibility_layout(request)
    return generate_recommendation(request)
