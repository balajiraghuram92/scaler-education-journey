"""Ported from api/Services/Exercises/ExerciseManifestModels.cs."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExerciseRuntimeManifest:
    profile: str = ""
    java_version: int = 0
    timeout_seconds: int = 0


@dataclass
class ExerciseFileManifest:
    id: str = ""
    path: str = ""
    display_name: str = ""
    editable: bool = False


@dataclass
class ExerciseTestSuiteManifest:
    visible: bool = False
    path: str = ""
    class_name: str = ""


@dataclass
class ExerciseEvidenceManifest:
    id: str = ""
    label: str = ""
    test_method: str = ""


@dataclass
class ExerciseManifest:
    id: str = ""
    lesson_slug: str = ""
    title: str = ""
    language: str = ""
    difficulty: str = ""
    estimated_minutes: int = 0
    instructions: str | None = None
    runtime: ExerciseRuntimeManifest = field(default_factory=ExerciseRuntimeManifest)
    files: list[ExerciseFileManifest] = field(default_factory=list)
    test_suite: ExerciseTestSuiteManifest = field(default_factory=ExerciseTestSuiteManifest)
    evidence: list[ExerciseEvidenceManifest] = field(default_factory=list)


@dataclass
class ExerciseDefinition:
    manifest: ExerciseManifest
    manifest_path: str
    exercise_root: str
    editable_files: dict[str, ExerciseFileManifest] = field(default_factory=dict)
    evidence_by_test_method: dict[str, ExerciseEvidenceManifest] = field(
        default_factory=dict
    )


class ExerciseRuntimeProfiles:
    JAVA_MAVEN = "java-maven"
    PYTHON_PYTEST = "python-pytest"

    @staticmethod
    def is_python(manifest: ExerciseManifest) -> bool:
        return manifest.runtime.profile.lower() == ExerciseRuntimeProfiles.PYTHON_PYTEST


def _get_case_insensitive(obj: dict[str, Any], name: str, default: Any = None) -> Any:
    for key, value in obj.items():
        if key.lower() == name.lower():
            return value
    return default


def parse_manifest(data: dict[str, Any]) -> ExerciseManifest:
    """Case-insensitive manifest parsing (C# uses PropertyNameCaseInsensitive)."""
    runtime_data = _get_case_insensitive(data, "runtime", {}) or {}
    test_suite_data = _get_case_insensitive(data, "testSuite", {}) or {}
    files_data = _get_case_insensitive(data, "files", []) or []
    evidence_data = _get_case_insensitive(data, "evidence", []) or []
    return ExerciseManifest(
        id=_get_case_insensitive(data, "id", "") or "",
        lesson_slug=_get_case_insensitive(data, "lessonSlug", "") or "",
        title=_get_case_insensitive(data, "title", "") or "",
        language=_get_case_insensitive(data, "language", "") or "",
        difficulty=_get_case_insensitive(data, "difficulty", "") or "",
        estimated_minutes=_get_case_insensitive(data, "estimatedMinutes", 0) or 0,
        instructions=_get_case_insensitive(data, "instructions"),
        runtime=ExerciseRuntimeManifest(
            profile=_get_case_insensitive(runtime_data, "profile", "") or "",
            java_version=_get_case_insensitive(runtime_data, "javaVersion", 0) or 0,
            timeout_seconds=_get_case_insensitive(runtime_data, "timeoutSeconds", 0) or 0,
        ),
        files=[
            ExerciseFileManifest(
                id=_get_case_insensitive(f, "id", "") or "",
                path=_get_case_insensitive(f, "path", "") or "",
                display_name=_get_case_insensitive(f, "displayName", "") or "",
                editable=bool(_get_case_insensitive(f, "editable", False)),
            )
            for f in files_data
        ],
        test_suite=ExerciseTestSuiteManifest(
            visible=bool(_get_case_insensitive(test_suite_data, "visible", False)),
            path=_get_case_insensitive(test_suite_data, "path", "") or "",
            class_name=_get_case_insensitive(test_suite_data, "className", "") or "",
        ),
        evidence=[
            ExerciseEvidenceManifest(
                id=_get_case_insensitive(e, "id", "") or "",
                label=_get_case_insensitive(e, "label", "") or "",
                test_method=_get_case_insensitive(e, "testMethod", "") or "",
            )
            for e in evidence_data
        ],
    )


def is_safe_relative_path(path: str | None) -> bool:
    if not path or not path.strip() or "\\" in path or ":" in path:
        return False
    if os.path.isabs(path):
        return False
    segments = path.split("/")
    return all(len(segment) > 0 and segment not in (".", "..") for segment in segments)


def resolve_inside(root: str, relative_path: str) -> str:
    if not is_safe_relative_path(relative_path):
        raise ValueError(f"Unsafe trusted exercise path '{relative_path}'.")
    # Lexical normalization like Path.GetFullPath (no symlink resolution).
    full_root = os.path.normpath(os.path.abspath(root))
    full_path = os.path.normpath(os.path.join(full_root, *relative_path.split("/")))
    root_with_sep = full_root if full_root.endswith(os.sep) else full_root + os.sep
    if os.name == "nt":
        inside = full_path.lower().startswith(root_with_sep.lower())
    else:
        inside = full_path.startswith(root_with_sep)
    if not inside:
        raise ValueError(
            f"Trusted exercise path '{relative_path}' escapes the exercise root."
        )
    return full_path


def is_link(path: str) -> bool:
    if os.path.islink(path):
        return True
    return _is_windows_reparse_point(path)


def _is_windows_reparse_point(path: str) -> bool:
    # C# also flags ReparsePoint (junctions); on Windows check the attribute.
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)  # type: ignore[attr-defined]
        return attrs != 0xFFFFFFFF and bool(attrs & 0x400)
    except OSError:
        return False
