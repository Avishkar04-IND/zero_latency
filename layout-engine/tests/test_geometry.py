import pytest
from app.geometry.geometry import Rect, compute_bounding_box


def test_rect_properties():
    r = Rect(10.0, 20.0, 30.0, 40.0)
    assert r.right == 40.0
    assert r.bottom == 60.0
    assert r.is_valid() is True


def test_rect_invalid_dimensions():
    assert Rect(0.0, 0.0, 0.0, 10.0).is_valid() is False
    assert Rect(0.0, 0.0, 10.0, -5.0).is_valid() is False


def test_rect_intersection():
    r1 = Rect(0.0, 0.0, 20.0, 20.0)
    r2 = Rect(10.0, 10.0, 20.0, 20.0)  # overlaps
    r3 = Rect(20.0, 0.0, 10.0, 20.0)   # adjacent edge, no overlap
    r4 = Rect(30.0, 30.0, 10.0, 10.0)  # completely separate

    assert r1.intersects(r2) is True
    assert r2.intersects(r1) is True
    assert r1.intersects(r3) is False
    assert r1.intersects(r4) is False


def test_rect_contains():
    outer = Rect(0.0, 0.0, 100.0, 50.0)
    inner = Rect(10.0, 10.0, 20.0, 20.0)
    overflow = Rect(90.0, 10.0, 20.0, 20.0)

    assert outer.contains(inner) is True
    assert outer.contains(overflow) is False
    assert inner.contains(outer) is False


def test_rect_margin():
    outer = Rect(0.0, 0.0, 100.0, 50.0)
    inner_ok = Rect(2.0, 2.0, 20.0, 20.0)
    inner_tight = Rect(0.5, 2.0, 20.0, 20.0)

    assert outer.has_min_margin(inner_ok, 1.0) is True
    assert outer.has_min_margin(inner_tight, 1.0) is False


def test_bounding_box():
    assert compute_bounding_box([]).width == 0.0

    rects = [
        Rect(10.0, 10.0, 10.0, 10.0),
        Rect(25.0, 5.0, 10.0, 20.0),
    ]
    bbox = compute_bounding_box(rects)
    assert bbox.x == 10.0
    assert bbox.y == 5.0
    assert bbox.right == 35.0
    assert bbox.bottom == 25.0
