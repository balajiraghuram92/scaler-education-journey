from __future__ import annotations

import ast
from collections.abc import Mapping


def _is_type_checking(test: ast.expr) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _module_level_imports(body: list[ast.stmt]) -> list[ast.Import | ast.ImportFrom]:
    """Imports that execute at import time: skips function bodies and TYPE_CHECKING blocks."""
    found: list[ast.Import | ast.ImportFrom] = []
    for node in body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            found.append(node)
        elif isinstance(node, ast.If):
            if not _is_type_checking(node.test):
                found += _module_level_imports(node.body)
            found += _module_level_imports(node.orelse)
        elif isinstance(node, ast.Try):
            for block in (node.body, node.orelse, node.finalbody, *(h.body for h in node.handlers)):
                found += _module_level_imports(block)
        elif isinstance(node, ast.ClassDef):
            found += _module_level_imports(node.body)
    return found


def _resolve_from(module: str, is_package: bool, level: int, name: str | None) -> str | None:
    if level == 0:
        return name
    parts = module.split(".")
    package = parts if is_package else parts[:-1]
    keep = len(package) - (level - 1)
    if keep <= 0:
        return None  # relative import beyond the top-level package
    base = package[:keep]
    return ".".join(base + ([name] if name else []))


def build_import_graph(sources: Mapping[str, str]) -> dict[str, set[str]]:
    """Map each project module to the project modules it imports at import time."""
    modules = set(sources)
    packages = {m for m in modules if any(o.startswith(m + ".") for o in modules)}
    graph: dict[str, set[str]] = {m: set() for m in modules}
    for module, source in sources.items():
        for node in _module_level_imports(ast.parse(source).body):
            targets: list[str] = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            else:
                base = _resolve_from(module, module in packages, node.level, node.module)
                if base is not None:
                    # "from pkg import name": an edge to pkg.name if that is a module, else to pkg
                    targets = [
                        f"{base}.{a.name}" if f"{base}.{a.name}" in modules else base
                        for a in node.names
                    ]
            for target in targets:
                # keep the longest known prefix: "pkg.mod.attr" -> "pkg.mod"
                parts = target.split(".")
                while parts and ".".join(parts) not in modules:
                    parts.pop()
                if parts and ".".join(parts) != module:
                    graph[module].add(".".join(parts))
    return graph


def find_cycles(graph: Mapping[str, set[str]]) -> list[list[str]]:
    """Strongly connected components with more than one module (Tarjan), sorted."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []
    counter = 0

    def visit(v: str) -> None:
        nonlocal counter
        index[v] = low[v] = counter
        counter += 1
        stack.append(v)
        on_stack.add(v)
        for w in sorted(graph.get(v, ())):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            if len(component) > 1:
                cycles.append(sorted(component))

    for v in sorted(graph):
        if v not in index:
            visit(v)
    return sorted(cycles)
