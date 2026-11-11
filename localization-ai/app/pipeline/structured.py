"""Shared structured-output helpers for the chat stages.

Fence-stripping plus JSON parsing/validation with a single ValueError shape,
so every stage's retry-once rule reads the same way.
"""

import json

from pydantic import BaseModel, ValidationError


def strip_fences(text: str) -> str:
    """Remove one surrounding markdown code fence (``` or ```json)."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    stripped = stripped[3:]
    if stripped.startswith("json"):
        stripped = stripped[4:]
    stripped = stripped.strip()
    if stripped.endswith("```"):
        stripped = stripped[:-3]
    return stripped.strip()


def parse_or_raise[M: BaseModel](text: str, model: type[M]) -> M:
    """Parse model output into ``model``; raises ValueError naming the problem."""
    try:
        data = json.loads(strip_fences(text))
    except json.JSONDecodeError as exc:
        raise ValueError(f"not valid JSON: {exc}") from None
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        first = exc.errors()[0]
        raise ValueError(f"JSON failed schema: {first['msg']} at {list(first['loc'])}") from None
