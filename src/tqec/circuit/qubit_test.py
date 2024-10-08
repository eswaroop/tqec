import re
from fractions import Fraction

import pytest
import stim

from tqec.circuit.qubit import (
    GridQubit,
    count_qubit_accesses,
    get_final_qubits,
    get_used_qubit_indices,
)
from tqec.exceptions import TQECException
from tqec.position import Displacement, Position2D


def test_grid_qubit_creation() -> None:
    GridQubit(0, 0)
    GridQubit(-1, 10)
    GridQubit(0.5, 10)
    GridQubit(1.5, -4.5)
    GridQubit(Fraction(1, 9), Fraction(0, 2))
    GridQubit(-Fraction(1, 9), -Fraction(0, 2))

    with pytest.raises(Exception):
        GridQubit(float("NaN"), 0.0)
    with pytest.raises(Exception):
        GridQubit(-float("inf"), 0.0)
    with pytest.raises(Exception):
        GridQubit(0.0, float("NaN"))


def test_grid_qubit_coordinates() -> None:
    assert GridQubit(0, 0).x == 0
    assert GridQubit(0, 0).y == 0
    assert GridQubit(-1, 10).x == -1
    assert GridQubit(-1, 10).y == 10
    assert GridQubit(0.5, 10).x == 0.5
    assert GridQubit(0.5, 10).y == 10
    assert GridQubit(Fraction(1, 9), Fraction(0, 2)).x == Fraction(1, 9)
    assert GridQubit(Fraction(1, 9), Fraction(0, 2)).y == 0


def test_grid_qubit_operators() -> None:
    q = GridQubit(0, 0)
    assert q + Displacement(0, 0) == q
    assert q + Position2D(0, 0) == q
    assert q + q == q
    assert q - Displacement(0, 0) == q
    assert q - Position2D(0, 0) == q
    assert q - q == q
    assert 3 * q == q
    assert q * 3 == q

    assert q + Displacement(1, 3) == GridQubit(1, 3)
    assert q + Position2D(1, 3) == GridQubit(1, 3)
    assert q + GridQubit(1, 3) == GridQubit(1, 3)

    q = GridQubit(-1, 0.5)
    assert q + Displacement(0, 0) == q
    assert q + q == 2 * q
    assert q - q == GridQubit(0, 0)


def test_grid_qubit_in_set() -> None:
    grid_qubits = [GridQubit(i, j) for i in range(10) for j in range(10)]
    assert len(set(grid_qubits)) == len(grid_qubits)
    assert len(set(grid_qubits + grid_qubits)) == len(grid_qubits)

    grid_qubits = [GridQubit(i / 3, 3 * j) for i in range(10) for j in range(10)]
    assert len(set(grid_qubits)) == len(grid_qubits)
    assert len(set(grid_qubits + grid_qubits)) == len(grid_qubits)


def test_grid_qubit_ordering() -> None:
    assert GridQubit(0, 0) < GridQubit(0, 1)
    assert GridQubit(0, 0) < GridQubit(1, 1)
    assert not GridQubit(0, 0) < GridQubit(-1, 1)
    assert not GridQubit(0, 0) < GridQubit(0, -1)


def test_count_qubit_accesses() -> None:
    assert count_qubit_accesses(stim.Circuit("H 0 1 2 3")) == {i: 1 for i in range(4)}
    assert count_qubit_accesses(stim.Circuit("QUBIT_COORDS(0, 0) 0")) == {}
    assert count_qubit_accesses(stim.Circuit("DETECTOR(0) rec[-1]")) == {}
    assert count_qubit_accesses(stim.Circuit("CX rec[-1] 0")) == {0: 1}
    assert count_qubit_accesses(stim.Circuit("H 0 0 1 1 2 2 3 3")) == {
        i: 2 for i in range(4)
    }
    assert count_qubit_accesses(stim.Circuit("H 0 1 2 3\nTICK\nH 0 1 2 3")) == {
        i: 2 for i in range(4)
    }
    assert count_qubit_accesses(
        stim.Circuit("REPEAT 34{\nH 0 1 2 3\nTICK\nH 0 1 2 3\n}")
    ) == {i: 34 * 2 for i in range(4)}


def test_used_qubit_indices() -> None:
    assert get_used_qubit_indices(stim.Circuit("H 0 1 2 3")) == frozenset(range(4))
    assert get_used_qubit_indices(stim.Circuit("QUBIT_COORDS(0, 0) 0")) == frozenset()
    assert get_used_qubit_indices(stim.Circuit("DETECTOR(0) rec[-1]")) == frozenset()
    assert get_used_qubit_indices(stim.Circuit("CX rec[-1] 0")) == frozenset([0])
    assert get_used_qubit_indices(stim.Circuit("H 0 0 1 1 2 2 3 3")) == frozenset(
        range(4)
    )
    assert get_used_qubit_indices(
        stim.Circuit("H 0 1 2 3\nTICK\nH 0 1 2 3")
    ) == frozenset(range(4))
    assert get_used_qubit_indices(
        stim.Circuit("REPEAT 34{\nH 0 1 2 3\nTICK\nH 0 1 2 3\n}")
    ) == frozenset(range(4))


def test_get_final_qubits() -> None:
    assert get_final_qubits(stim.Circuit("QUBIT_COORDS(0, 0) 0")) == {
        0: GridQubit(0, 0)
    }
    assert get_final_qubits(stim.Circuit("QUBIT_COORDS(0, 0.5) 0")) == {
        0: GridQubit(0, 0.5)
    }
    assert get_final_qubits(stim.Circuit("QUBIT_COORDS(0, 0) 1")) == {
        1: GridQubit(0, 0)
    }
    # assert get_final_qubits(
    #     stim.Circuit("QUBIT_COORDS(0, 0) 0\nQUBIT_COORDS(1, 4) 0")
    # ) == {0: GridQubit(1, 4)}
    assert get_final_qubits(
        stim.Circuit("QUBIT_COORDS(0, 0) 0\nQUBIT_COORDS(1, 4) 1")
    ) == {0: GridQubit(0, 0), 1: GridQubit(1, 4)}

    with pytest.raises(
        TQECException,
        match=re.escape(
            "Qubits should be defined on exactly 2 spatial dimensions. "
            f"Found {0} -> [0.0, 0.0, 1.0] defined on 3 spatial dimensions."
        ),
    ):
        get_final_qubits(stim.Circuit("QUBIT_COORDS(0, 0, 1) 0"))