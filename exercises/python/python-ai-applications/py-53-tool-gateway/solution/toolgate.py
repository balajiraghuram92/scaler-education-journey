from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ValidationError

log = logging.getLogger(__name__)

Status = Literal["ok", "invalid_arguments", "unknown_tool", "forbidden", "needs_approval", "error"]


@dataclass(frozen=True, slots=True)
class Ctx:
    """Authenticated identity. Built by the server, never parsed from model output."""
    tenant_id: str
    scopes: frozenset[str]


@dataclass(frozen=True, slots=True)
class Observation:
    status: Status
    content: str


@dataclass(frozen=True, slots=True)
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
        if tool.name in self._tools:
            raise ValueError(f"duplicate tool {tool.name!r}")
        if tool.args_model.model_config.get("extra") != "forbid":
            raise ValueError(f"{tool.name}: args model must set extra='forbid'")
        self._tools[tool.name] = tool

    def definitions(self) -> list[dict]:
        return [
            {"type": "function",
             "function": {"name": t.name, "description": t.description,
                          "parameters": t.args_model.model_json_schema()}}
            for t in self._tools.values()
        ]

    def call(self, name: str, arguments: str, ctx: Ctx, *, approved: bool = False) -> Observation:
        tool = self._tools.get(name)
        if tool is None:
            return Observation("unknown_tool",
                               f"unknown tool {name!r}; available: {', '.join(sorted(self._tools))}")
        if tool.scope not in ctx.scopes:
            return Observation("forbidden", f"tool {name!r} is not permitted for this session")
        try:
            args = tool.args_model.model_validate_json(arguments)
        except ValidationError as exc:
            problems = [f"{'.'.join(map(str, e['loc'])) or '<root>'}: {e['msg']}"
                        for e in exc.errors(include_url=False)[:3]]
            return Observation("invalid_arguments", "; ".join(problems))
        if tool.needs_approval and not approved:
            return Observation("needs_approval", f"{name} requires human approval")
        try:
            return Observation("ok", tool.handler(args, ctx))
        except Exception:                                   # noqa: BLE001 - boundary
            log.exception("tool %s failed", name)
            return Observation("error", f"tool {name!r} failed")
