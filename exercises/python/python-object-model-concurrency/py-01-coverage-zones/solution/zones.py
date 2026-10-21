import math


class Zone:
    def __init__(self, name):
        self.name = name

    def area(self):
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, Zone):
            return NotImplemented
        return self.area() == other.area()

    def __lt__(self, other):
        if not isinstance(other, Zone):
            return NotImplemented
        return self.area() < other.area()

    def __add__(self, other):
        if not isinstance(other, Zone):
            return NotImplemented
        total = self.area() + other.area()

        zone = Zone(f"{self.name}+{other.name}")
        zone.area = lambda: total

        return zone


class CircularZone(Zone):
    def __init__(self, name, radius):
        super().__init__(name)
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2


class RectangularZone(Zone):
    def __init__(self, name, width, height):
        super().__init__(name)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class TriangularZone(Zone):
    def __init__(self, name, base, height):
        super().__init__(name)
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height
