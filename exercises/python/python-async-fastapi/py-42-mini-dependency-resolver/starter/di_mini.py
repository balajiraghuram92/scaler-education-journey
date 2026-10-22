from __future__ import annotations

import inspect
from collections.abc import Callable
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any


class Depends:
    """Marker used as a parameter default: ``def endpoint(db=Depends(get_db))``."""

    def __init__(self, dependency: Callable[..., Any], *, use_cache: bool = True) -> None:
        self.dependency = dependency
        self.use_cache = use_cache


class CircularDependencyError(Exception):
    """Raised for a dependency cycle; the message lists the chain, e.g. ``a -> b -> a``."""


class Resolver:
    """Framework-free version of FastAPI's dependency resolution.

    Requirements:
    - a parameter whose default is a ``Depends`` is resolved recursively; otherwise it is filled
      from ``values`` if present, else it keeps its own default, else raise ``TypeError`` naming
      the missing parameter
    - dependencies may be plain functions, ``async def`` functions or ``async def`` generator
      functions (``inspect.isasyncgenfunction`` + ``AsyncExitStack``); generators are torn down in
      reverse order of setup, and an exception raised by the endpoint is thrown into each
      generator at its ``yield``
    - the cache lives for one ``run`` call only and is keyed by the *original* callable
      (``use_cache=False`` calls the dependency again)
    - an override replaces the callable that is actually invoked, but the replacement's own
      parameters are resolved normally
    - a cycle raises ``CircularDependencyError``
    """

    def __init__(self, overrides: dict[Callable[..., Any], Callable[..., Any]] | None = None) -> None:
        """``overrides`` maps an original dependency callable to its replacement."""
        raise NotImplementedError("Implement Resolver.__init__")

    async def run(self, endpoint: Callable[..., Any], **values: Any) -> Any:
        """Resolve the endpoint's dependencies, call it, tear everything down, return its result."""
        raise NotImplementedError("Implement Resolver.run")
