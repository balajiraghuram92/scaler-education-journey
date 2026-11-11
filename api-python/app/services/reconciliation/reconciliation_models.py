"""Ported from api/Services/Reconciliation/ReconciliationModels.cs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from ...stjson import dumps as _json_dumps


class ReconciliationExecutionMode(StrEnum):
    DRY_RUN = "DryRun"
    APPLY = "Apply"
    VERIFY = "Verify"


@dataclass
class ReconciliationOptions:
    scope: str = "all"  # java, fde, azure, labs, atlas, reading-map, knowledge-threads, all
    mode: ReconciliationExecutionMode = ReconciliationExecutionMode.DRY_RUN


@dataclass
class MappingCandidate:
    legacy_task_id: int = 0
    legacy_title: str = ""
    legacy_module: str = ""
    legacy_is_completed: bool = False
    target_lesson_id: int | None = None
    target_problem_id: int | None = None
    target_title: str = ""
    mapping_type: str = "TitleAndModule"  # Exact, TitleAndModule, Manual, DuplicateAlias
    mapping_status: str = "Proposed"  # Proposed, Verified, Rejected, Conflict
    confidence: Decimal = Decimal("1.0000")
    source_checksum: str = ""
    issue_code: str | None = None
    note: str | None = None

    def to_details_json(self) -> str:
        # System.Text.Json default options: PascalCase keys, declaration order,
        # decimals with scale preserved (1.0000, not 1.0).
        payload = _json_dumps(
            {
                "LegacyTaskId": self.legacy_task_id,
                "LegacyTitle": self.legacy_title,
                "LegacyModule": self.legacy_module,
                "LegacyIsCompleted": self.legacy_is_completed,
                "TargetLessonId": self.target_lesson_id,
                "TargetProblemId": self.target_problem_id,
                "TargetTitle": self.target_title,
                "MappingType": self.mapping_type,
                "MappingStatus": self.mapping_status,
                "Confidence": "@@CONFIDENCE@@",
                "SourceChecksum": self.source_checksum,
                "IssueCode": self.issue_code,
                "Note": self.note,
            }
        )
        return payload.replace('"@@CONFIDENCE@@"', f"{self.confidence:.4f}")


@dataclass
class ReconciliationReport:
    scope: str = ""
    mode: ReconciliationExecutionMode = ReconciliationExecutionMode.DRY_RUN
    executed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    discovered_count: int = 0
    exact_mapped_count: int = 0
    proposed_count: int = 0
    verified_count: int = 0
    conflict_count: int = 0
    skipped_count: int = 0
    mappings: list[MappingCandidate] = field(default_factory=list)
    audit_log: list[str] = field(default_factory=list)
