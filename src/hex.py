'''
Representation of hexagonal coordinate system
based on: https://www.redblobgames.com/grids/hexagons/#distances
'''
from __future__ import annotations


class Cube:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def distance(self, other: Cube) -> int:
        return max(abs(self.x - other.x), abs(self.y - other.y), abs(self.z - other.z))

    @classmethod
    def from_axial(cls, q: int, r: int) -> Cube:
        return cls(q, -q - r, r)

    @classmethod
    def from_board_array(cls, x: int, y: int) -> Cube:
        q = x - y if y < 5 else x - 4
        r = y
        return cls.from_axial(q, r)


class Axial:
    def __init__(self, q: int, r: int):
        self.q = q
        self.r = r

    def to_cube(self) -> Cube:
        x = self.q
        z = self.r
        y = -x-z
        return Cube(x, y, z)
