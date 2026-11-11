"""Task types. Callers ask for a task type, never for a model name."""
from __future__ import annotations

from enum import StrEnum


class TaskType(StrEnum):
    TICKET_PARSE = "ticket_parse"
    MODULE_CHECK = "module_check"
    RELEVANCE = "relevance"
    SYNTHESIS = "synthesis"
    OUTCOME_CLASSIFY = "outcome_classify"
    FIX_PLAN = "fix_plan"
    FIX_PATCH = "fix_patch"
    CONFLICT_RESOLVE = "conflict_resolve"
    QUALITY_VERIFY = "quality_verify"
    FINAL_CHECK = "final_check"
    EMBED = "embed"
