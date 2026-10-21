import math


class Zone:
    """Base class of every service-coverage zone.

    - ``area()`` raises ``NotImplementedError`` on the base class; shapes override it.
    - ``__eq__``: zones are equal when their areas are equal.
    - ``__lt__``: a zone is smaller when its area is smaller (so ``sorted(zones)`` works).
    - ``__add__``: returns a NEW ``Zone`` whose ``area()`` is the sum of both areas.
    - Write the comparisons in terms of ``area()`` so subclasses only implement ``area``.
    - For operands that are not zones, return ``NotImplemented`` instead of raising.
    """

    def __init__(self, name):
        self.name = name

    def area(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError("Implement Zone.__eq__")

    def __lt__(self, other):
        raise NotImplementedError("Implement Zone.__lt__")

    def __add__(self, other):
        raise NotImplementedError("Implement Zone.__add__")


class CircularZone(Zone):
    """``CircularZone(name, radius)``: area is ``math.pi * radius ** 2``."""

    def __init__(self, name, radius):
        raise NotImplementedError("Implement CircularZone.__init__")

    def area(self):
        raise NotImplementedError("Implement CircularZone.area")


class RectangularZone(Zone):
    """``RectangularZone(name, width, height)``: area is ``width * height``."""

    def __init__(self, name, width, height):
        raise NotImplementedError("Implement RectangularZone.__init__")

    def area(self):
        raise NotImplementedError("Implement RectangularZone.area")


class TriangularZone(Zone):
    """``TriangularZone(name, base, height)``: area is ``0.5 * base * height``."""

    def __init__(self, name, base, height):
        raise NotImplementedError("Implement TriangularZone.__init__")

    def area(self):
        raise NotImplementedError("Implement TriangularZone.area")
