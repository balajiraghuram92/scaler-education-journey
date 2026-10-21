from __future__ import annotations

import inspect
from collections.abc import Callable
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any


class Depends:
    def __init__(self, dependency: Callable[..., Any], *, use_cache: bool = True) -> None:
        self.dependency = dependency
        self.use_cache = use_cache


class CircularDependencyError(Exception):
    pass


class Resolver:
    def __init__(self, overrides: dict[Callable[..., Any], Callable[..., Any]] | None = None) -> None:
        self._overrides = overrides or {}

    async def run(self, endpoint: Callable[..., Any], **values: Any) -> Any:
        cache: dict[Callable[..., Any], Any] = {}
        async with AsyncExitStack() as stack:
            kwargs = await self._kwargs(endpoint, values, cache, stack, ())
            return await self._invoke(endpoint, kwargs, stack)

    async def _kwargs(
        self,
        fn: Callable[..., Any],
        values: dict[str, Any],
        cache: dict[Callable[..., Any], Any],
        stack: AsyncExitStack,
        path: tuple[Callable[..., Any], ...],
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        for name, param in inspect.signature(fn).parameters.items():
            if isinstance(param.default, Depends):
                kwargs[name] = await self._resolve(param.default, cache, stack, path)
            elif name in values:
                kwargs[name] = values[name]
            elif param.default is inspect.Parameter.empty:
                raise TypeError(f"missing value for parameter {name!r} of {fn.__name__}")
        return kwargs

    async def _resolve(
        self,
        dep: Depends,
        cache: dict[Callable[..., Any], Any],
        stack: AsyncExitStack,
        path: tuple[Callable[..., Any], ...],
    ) -> Any:
        original = dep.dependency
        if original in path:
            raise CircularDependencyError(" -> ".join(f.__name__ for f in (*path, original)))
        if dep.use_cache and original in cache:
            return cache[original]
        actual = self._overrides.get(original, original)
        kwargs = await self._kwargs(actual, {}, cache, stack, (*path, original))
        value = await self._invoke(actual, kwargs, stack)
        cache.setdefault(original, value)
        return value

    @staticmethod
    async def _invoke(fn: Callable[..., Any], kwargs: dict[str, Any], stack: AsyncExitStack) -> Any:
        if inspect.isasyncgenfunction(fn):
            return await stack.enter_async_context(asynccontextmanager(fn)(**kwargs))
        result = fn(**kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result
