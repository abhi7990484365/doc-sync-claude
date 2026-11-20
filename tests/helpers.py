"""Small shared test helpers."""

import ast
from types import ModuleType


def imported_modules(module: ModuleType) -> set[str]:
    """Return the top-level names imported by a module's source (via ast)."""
    with open(module.__file__, encoding="utf-8") as handle:  # type: ignore[arg-type]
        tree = ast.parse(handle.read())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names
