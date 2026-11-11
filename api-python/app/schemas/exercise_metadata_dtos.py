"""Ported from api/Models/ExerciseMetadataDtos.cs."""

from __future__ import annotations

from .base import CamelModel


class ExerciseFileMetadataDto(CamelModel):
    id: str = ""
    path: str = ""
    display_name: str = ""
    editable: bool = False
    starter_content: str = ""


class ExerciseEvidenceMetadataDto(CamelModel):
    id: str = ""
    label: str = ""


class ExerciseMetadataResponse(CamelModel):
    id: str = ""
    lesson_slug: str = ""
    title: str = ""
    language: str = ""
    difficulty: str = ""
    estimated_minutes: int = 0
    instructions: str | None = None
    files: list[ExerciseFileMetadataDto] = []
    evidence: list[ExerciseEvidenceMetadataDto] = []


class ExerciseSolutionFileDto(CamelModel):
    id: str = ""
    path: str = ""
    display_name: str = ""
    language: str = ""
    content: str = ""
    display_order: int = 0


class ExerciseSolutionResponse(CamelModel):
    exercise_id: str = ""
    files: list[ExerciseSolutionFileDto] = []
