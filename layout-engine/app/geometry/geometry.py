from dataclasses import dataclass
import math
from typing import Optional, Sequence, Tuple


@dataclass(frozen=True)
class Rect:
    """Axis-aligned rectangle in 2D millimeter space."""

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def area(self) -> float:
        """Returns physical area in square millimeters."""
        return max(0.0, self.width) * max(0.0, self.height)

    def is_valid(self) -> bool:
        return self.width > 0.0 and self.height > 0.0

    def intersects(self, other: "Rect") -> bool:
        """Returns True if this rectangle overlaps with another rectangle with non-zero area."""
        return not (
            self.right <= other.x
            or other.right <= self.x
            or self.bottom <= other.y
            or other.bottom <= self.y
        )

    def intersection(self, other: "Rect") -> Optional["Rect"]:
        """Returns intersection rectangle if two rectangles overlap with positive area, else None."""
        if not self.intersects(other):
            return None
        ix = max(self.x, other.x)
        iy = max(self.y, other.y)
        iw = min(self.right, other.right) - ix
        ih = min(self.bottom, other.bottom) - iy
        return Rect(ix, iy, iw, ih)

    def contains(self, other: "Rect") -> bool:
        """Returns True if this rectangle completely encloses the other rectangle."""
        return (
            self.x <= other.x
            and self.y <= other.y
            and self.right >= other.right
            and self.bottom >= other.bottom
        )

    def has_min_margin(self, other: "Rect", min_margin: float) -> bool:
        """Returns True if other is inside this rectangle with at least min_margin clearance on all sides."""
        return (
            other.x - self.x >= min_margin
            and other.y - self.y >= min_margin
            and self.right - other.right >= min_margin
            and self.bottom - other.bottom >= min_margin
        )

    def distance_to(self, other: "Rect") -> float:
        """Calculates minimum Euclidean distance to another rectangle (0.0 if touching or overlapping)."""
        dx = max(0.0, max(self.x, other.x) - min(self.right, other.right))
        dy = max(0.0, max(self.y, other.y) - min(self.bottom, other.bottom))
        return math.hypot(dx, dy)


def compute_bounding_box(rects: Sequence[Rect]) -> Rect:
    """Computes minimal enclosing bounding box for a sequence of rectangles."""
    if not rects:
        return Rect(0.0, 0.0, 0.0, 0.0)
    min_x = min(r.x for r in rects)
    min_y = min(r.y for r in rects)
    max_x = max(r.right for r in rects)
    max_y = max(r.bottom for r in rects)
    return Rect(min_x, min_y, max_x - min_x, max_y - min_y)


def can_fit_in_area(
    available_area: Rect,
    item_width_mm: float,
    item_height_mm: float,
    allow_rotation: bool = True,
) -> Tuple[bool, float]:
    """Determines whether an element with dimensions item_width_mm x item_height_mm fits in available_area.

    Returns:
        (fits, rotation_degrees): (True, 0.0) if fits without rotation,
                                 (True, 90.0) if fits with 90° rotation,
                                 (False, 0.0) if cannot fit.
    """
    if item_width_mm <= 0.0 or item_height_mm <= 0.0 or not available_area.is_valid():
        return False, 0.0

    # Test 0° / 180°
    if item_width_mm <= available_area.width and item_height_mm <= available_area.height:
        return True, 0.0

    # Test 90° / 270°
    if allow_rotation and item_height_mm <= available_area.width and item_width_mm <= available_area.height:
        return True, 90.0

    return False, 0.0


def calculate_tablet_marking_area(
    tablet_width_mm: float,
    tablet_height_mm: Optional[float] = None,
    is_round: bool = False,
    safety_margin_mm: float = 0.5,
) -> Rect:
    """Calculates the usable physical marking area on a tablet face in millimeters.

    For round tablets, uses the inscribed bounding box inside the usable circle.
    For non-round/caplet tablets, subtracts safety margins from width and height.
    """
    if is_round or tablet_height_mm is None:
        # Inscribed square inside circle of usable diameter (D - 2*margin)
        usable_diameter = max(0.0, tablet_width_mm - 2.0 * safety_margin_mm)
        inscribed_side = usable_diameter / math.sqrt(2.0)
        return Rect(safety_margin_mm, safety_margin_mm, inscribed_side, inscribed_side)

    usable_w = max(0.0, tablet_width_mm - 2.0 * safety_margin_mm)
    usable_h = max(0.0, tablet_height_mm - 2.0 * safety_margin_mm)
    return Rect(safety_margin_mm, safety_margin_mm, usable_w, usable_h)


def mm_to_pixels(mm: float, dpi: float) -> float:
    """Converts physical millimeters to pixels at a given DPI resolution."""
    if dpi <= 0.0:
        raise ValueError("DPI must be strictly greater than 0")
    return mm * dpi / 25.4


def pixels_to_mm(pixels: float, dpi: float) -> float:
    """Converts pixels to physical millimeters at a given DPI resolution."""
    if dpi <= 0.0:
        raise ValueError("DPI must be strictly greater than 0")
    return pixels * 25.4 / dpi
