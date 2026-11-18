"""NFR-1: every function/method in doc_sync has fully annotated signatures."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from collections.abc import Callable, Iterator
from types import ModuleType

import doc_sync

SELF_NAMES = frozenset({"self", "cls"})


def load_modules() -> list[ModuleType]:
    """Import the package and every module in it."""
    modules = [doc_sync]
    for info in pkgutil.iter_modules(doc_sync.__path__, "doc_sync."):
        modules.append(importlib.import_module(info.name))
    return modules


def unwrap(member: object, filename: str) -> Callable[..., object] | None:
    """Return the function of a member if it is written in `filename`.

    Code synthesised elsewhere (dataclass __eq__/__repr__ etc.) is excluded.
    """
    if isinstance(member, (staticmethod, classmethod)):
        member = member.__func__
    elif isinstance(member, property):
        member = member.fget
    if not inspect.isfunction(member) or member.__code__.co_filename != filename:
        return None
    return member


def iter_functions(module: ModuleType) -> Iterator[tuple[str, Callable[..., object]]]:
    """Yield (qualified name, function) defined in the module itself."""
    filename = str(module.__file__)
    for name, obj in vars(module).items():
        func = unwrap(obj, filename)
        if func is not None and func.__module__ == module.__name__:
            yield f"{module.__name__}.{name}", func
        elif inspect.isclass(obj) and obj.__module__ == module.__name__:
            for mname, member in vars(obj).items():
                mfunc = unwrap(member, filename)
                if mfunc is not None:
                    yield f"{module.__name__}.{name}.{mname}", mfunc


def missing_annotations(func: Callable[..., object]) -> list[str]:
    """List parameters (and 'return') lacking an annotation."""
    sig = inspect.signature(func)
    missing = [
        p.name
        for p in sig.parameters.values()
        if p.name not in SELF_NAMES and p.annotation is inspect.Parameter.empty
    ]
    if sig.return_annotation is inspect.Signature.empty:
        missing.append("return")
    return missing


def find_violations(modules: list[ModuleType]) -> tuple[int, list[str]]:
    """Return (functions examined, violation messages)."""
    count = 0
    problems: list[str] = []
    for module in modules:
        for qualname, func in iter_functions(module):
            count += 1
            missing = missing_annotations(func)
            if missing:
                problems.append(f"{qualname}: missing {', '.join(missing)}")
    return count, problems


def test_checker_reports_missing_annotation() -> None:
    def bad(a, b: int):  # type: ignore[no-untyped-def]
        return a

    def good(self, a: int) -> None:  # type: ignore[no-untyped-def]
        return None

    assert missing_annotations(bad) == ["a", "return"]
    assert missing_annotations(good) == []


def test_checker_reports_violation_in_module() -> None:
    fake = ModuleType("fake_mod")
    fake.__file__ = __file__

    def bad(x):  # type: ignore[no-untyped-def]
        return x

    bad.__module__ = "fake_mod"
    fake.bad = bad  # type: ignore[attr-defined]
    count, problems = find_violations([fake])
    assert count == 1
    assert problems == ["fake_mod.bad: missing x, return"]


def test_modules_discovered() -> None:
    names = {m.__name__ for m in load_modules()}
    assert {"doc_sync", "doc_sync.cli", "doc_sync.render"} <= names


def test_all_signatures_annotated() -> None:
    count, problems = find_violations(load_modules())
    assert count > 0
    assert problems == []
