from __future__ import annotations

from collections.abc import Mapping


def build_import_graph(sources: Mapping[str, str]) -> dict[str, set[str]]:
    """Map each project module to the project modules it imports AT IMPORT TIME (use the ``ast`` module).

    - ``sources`` is ``{dotted_module_name: source_text}``; every key appears in the graph, even with no edges
    - a module is a PACKAGE if another key starts with ``"<name>."``
    - edges only point to project modules (keys of ``sources``); stdlib / third-party imports and self-edges are dropped
    - ``import a.b.c`` -> edge to the longest known module prefix
    - ``from pkg import name`` -> edge to ``pkg.name`` if that is a module, otherwise to ``pkg``
    - relative imports (``node.level`` dots, ``node.module`` may be None) resolve against the importing module's
      package (for a package module that is the module itself); one that climbs above the top-level package is ignored
    - ignore imports inside function bodies and inside ``if TYPE_CHECKING:`` blocks; imports in ``try`` / ``except``,
      other ``if`` blocks (and ``else`` branches) and class bodies do count
    """
    raise NotImplementedError("Implement build_import_graph")


def find_cycles(graph: Mapping[str, set[str]]) -> list[list[str]]:
    """Every strongly connected component with more than one module, as a sorted list; components sorted too.

    Use Tarjan's or Kosaraju's algorithm.
    """
    raise NotImplementedError("Implement find_cycles")
