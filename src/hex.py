'''
Representation of hexagonal coordinate system
based on: https://www.redblobgames.com/grids/hexagons
'''
from __future__ import annotations

from typing import Tuple


class Cube:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_axial(cls, q: int, r: int) -> Cube:
        return cls(q, -q - r, r)

    @classmethod
    def from_board_array(cls, x: int, y: int) -> Cube:
        q = x - y if y < 5 else x - 4
        r = y
        return cls.from_axial(q, r)

    def to_board_array(self) -> Tuple[int, int]:
        # to axial
        q = self.x
        r = self.z
        # to board array
        y = r
        x = q + y if y < 5 else q + 4
        return (x, y)

    def copy(self) -> Cube:
        return Cube(self.x, self.y, self.z)

    def add(self, other: Cube) -> Cube:
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    @classmethod
    def neighbor_indices(cls):
        return [
            (+1, -1, 0), (+1, 0, -1), (0, +1, -
                                       1), (-1, +1, 0), (-1, 0, +1), (0, -1, +1)
        ]

    def distance(self, other: Cube) -> int:
        return max(abs(self.x - other.x), abs(self.y - other.y), abs(self.z - other.z))


class Axial:
    def __init__(self, q: int, r: int):
        self.q = q
        self.r = r

    def to_cube(self) -> Cube:
        x = self.q
        z = self.r
        y = -x-z
        return Cube(x, y, z)
