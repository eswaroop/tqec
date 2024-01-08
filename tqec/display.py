import numpy

from tqec.generation.topology import get_qubit_array_str
from tqec.templates.base import Template
from tqec.templates.orchestrator import TemplateOrchestrator


def display_template(template: Template | TemplateOrchestrator, *plaquette_indices: int) -> None:
    """Display a template instance with ASCII output.

    :param template: the Template instance to display.
    :param plaquette_indices: the plaquette indices that are forwarded to the
        call to template.instanciate to get the actual template representation.
    """
    if isinstance(template, TemplateOrchestrator) and len(plaquette_indices) == 0:
        plaquette_indices = tuple(range(template.expected_plaquettes_number))
    arr = template.instanciate(*plaquette_indices)
    for line in arr:
        for element in line:
            element = str(element) if element != 0 else "."
            print(f"{element:>3}", end="")
        print()


def display_qubit_array(
    array: numpy.ndarray, qubit_str: str = "x", nothing_str: str = " "
) -> None:
    """Display a qubit array with ASCII output."""
    print(get_qubit_array_str(array, qubit_str, nothing_str))