from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

log = logging.getLogger(__name__)

Status = Literal["ok", "invalid_arguments", "unknown_tool", "forbidden", "needs_approval", "error"]


# TODO: Ctx, Observation and Tool must be frozen, slotted dataclasses.
@dataclass
class Ctx:
    """Authenticated identity. Built by the server, never parsed from model output."""

    tenant_id: str
    scopes: frozenset[str]


@dataclass
class Observation:
    status: Status
    content: str


@dataclass
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    handler: Callable[[BaseModel, Ctx], str]
    scope: str
    needs_approval: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Raise ``ValueError`` for a duplicate name, and for an args model whose
        ``model_config["extra"]`` is not ``"forbid"``."""
        raise NotImplementedError("Implement ToolRegistry.register")

    def definitions(self) -> list[dict]:
        """Chat-completions style definitions:
        ``{"type": "function", "function": {"name", "description", "parameters": <JSON Schema>}}``
        where ``parameters`` comes from the Pydantic model."""
        raise NotImplementedError("Implement ToolRegistry.definitions")

    def call(self, name: str, arguments: str, ctx: Ctx, *, approved: bool = False) -> Observation:
        """Check, in this order:

        1. unknown tool -> ``unknown_tool`` (message lists available names, sorted)
        2. ``tool.scope in ctx.scopes`` else ``forbidden`` (before parsing the arguments)
        3. ``model_validate_json(arguments)``; failures -> ``invalid_arguments`` with at most
           3 problems formatted ``loc: message`` and joined by ``"; "`` (non-object JSON and
           non-JSON text included); the handler is never invoked
        4. ``needs_approval`` and not ``approved`` -> ``needs_approval``
        5. run the handler; if it raises, log it server-side and return
           ``Observation("error", "tool '<name>' failed")`` without the exception text
        """
        raise NotImplementedError("Implement ToolRegistry.call")
