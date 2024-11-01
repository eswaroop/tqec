from __future__ import annotations

from dataclasses import astuple, dataclass
from enum import Enum

from tqec.exceptions import TQECException


@dataclass(frozen=True)
class Position2D:
    """Simple wrapper around tuple[int, int].

    This class is here to explicitly name the type of variables as positions
    instead of having a tuple[int, int] that could be:
    - a position,
    - a shape,
    - coefficients for positions,
    - displacements.
    """

    x: int
    y: int

    def to_grid_qubit(self) -> tuple[int, int]:
        """Returns the position as a tuple following the cirq.GridQubit
        coordinate system."""
        return (self.y, self.x)


@dataclass(frozen=True)
class Shape2D:
    """Simple wrapper around tuple[int, int].

    This class is here to explicitly name the type of variables as shapes
    instead of having a tuple[int, int] that could be:
    - a position,
    - a shape,
    - coefficients for positions,
    - displacements.
    """

    x: int
    y: int

    def to_numpy_shape(self) -> tuple[int, int]:
        """Returns the shape according to numpy indexing.

        In the coordinate system used in this library, numpy indexes
        arrays using (y, x) coordinates. This method is here to
        translate a Shape instance to a numpy shape transparently for
        the user.
        """
        return (self.y, self.x)


@dataclass(frozen=True)
class Displacement:
    """Simple wrapper around tuple[int, int].

    This class is here to explicitly name the type of variables as displacements
    instead of having a tuple[int, int] that could be:
    - a position,
    - a shape,
    - coefficients for positions,
    - displacements.
    """

    x: int
    y: int

    def __mul__(self, factor: int) -> Displacement:
        return Displacement(factor * self.x, factor * self.y)

    def __rmul__(self, factor: int) -> Displacement:
        return self.__mul__(factor)


@dataclass(frozen=True, order=True)
class Position3D:
    """A 3D integer position."""

    x: int
    y: int
    z: int

    def __post_init__(self) -> None:
        if any(not isinstance(i, int) for i in astuple(self)):
            raise TQECException("Position must be an integer.")

    def shift_by(self, dx: int = 0, dy: int = 0, dz: int = 0) -> Position3D:
        """Shift the position by the given offset."""
        return Position3D(self.x + dx, self.y + dy, self.z + dz)

    def is_neighbour(self, other: Position3D) -> bool:
        """Check if the other position is near to this position, i.e. Manhattan
        distance is 1."""
        return (
            abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z) == 1
        )

    def as_tuple(self) -> tuple[int, int, int]:
        """Return the position as a tuple."""
        return astuple(self)

    def __str__(self) -> str:
        return f"({self.x},{self.y},{self.z})"

    def as_2d(self) -> Position2D:
        """Return the position as a 2D position."""
        return Position2D(self.x, self.y)


class Direction3D(Enum):
    """Axis directions in the 3D spacetime diagram."""

    X = 0
    Y = 1
    Z = 2

    @staticmethod
    def all() -> list[Direction3D]:
        """Get all directions."""
        return [e for e in Direction3D]

    @staticmethod
    def from_axis_index(i: int) -> Direction3D:
        """Get the direction from the axis index."""
        if i not in [d.value for d in Direction3D]:
            raise TQECException(f"Invalid axis index: {i}")
        return Direction3D.all()[i]

    @property
    def axis_index(self) -> int:
        """Get the axis index."""
        return self.value

    def __str__(self) -> str:
        return self.name
