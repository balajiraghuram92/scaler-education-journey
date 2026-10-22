import math

import pytest

from zones import CircularZone, RectangularZone, TriangularZone, Zone


def test_shape_areas():
    assert CircularZone("C", 2).area() == pytest.approx(math.pi * 4), "circle area is pi * r**2"
    assert RectangularZone("R", 4, 5).area() == 20, "rectangle area is width * height"
    assert TriangularZone("T", 6, 4).area() == 12, "triangle area is 0.5 * base * height"


def test_base_zone_has_no_area():
    with pytest.raises(NotImplementedError):
        Zone("Z").area()


def test_shapes_keep_their_name_and_extend_zone():
    for z in (CircularZone("c", 1), RectangularZone("r", 1, 1), TriangularZone("t", 1, 1)):
        assert isinstance(z, Zone), "every shape must extend Zone"
    assert CircularZone("c", 3).name == "c" and CircularZone("c", 3).radius == 3


def test_equality_is_by_area_across_shapes():
    assert RectangularZone("R", 2, 3) == TriangularZone("T", 4, 3), "6 == 6.0, shape must not matter"
    assert RectangularZone("R", 2, 3) != RectangularZone("R2", 2, 4), "areas 6 and 8 differ"


def test_sorted_orders_zones_by_area():
    zones = [RectangularZone("A", 5, 5), TriangularZone("B", 4, 2), CircularZone("C", 1)]
    assert [z.name for z in sorted(zones)] == ["C", "B", "A"], "sorted() must use __lt__ on areas"


def test_lt_and_derived_comparison():
    small, big = TriangularZone("s", 1, 1), RectangularZone("b", 3, 3)
    assert small < big and not big < small, "__lt__ compares areas"
    assert max(small, big) is big, "max() works through __lt__"


def test_add_returns_new_zone_with_summed_area():
    r, t = RectangularZone("R", 4, 5), TriangularZone("T", 6, 4)
    total = r + t
    assert isinstance(total, Zone), "the sum must be a Zone"
    assert total.area() == 32.0, "20 + 12 = 32"
    assert r.area() == 20 and t.area() == 12, "operands must not be modified"
    assert total is not r and total is not t


def test_sum_zone_can_be_added_and_compared_again():
    a, b, c = RectangularZone("a", 1, 2), RectangularZone("b", 1, 3), RectangularZone("c", 1, 1)
    total = a + b + c
    assert total.area() == 6, "(a + b) + c keeps adding areas"
    assert total == RectangularZone("six", 2, 3), "a combined zone compares by area like any other"


def test_non_zone_operands_are_handled_politely():
    z = RectangularZone("R", 2, 2)
    assert (z == 4) is False, "== with a non-zone must be False, not raise AttributeError"
    assert z != "zone"
    with pytest.raises(TypeError):
        z < 5
    with pytest.raises(TypeError):
        z + 5
