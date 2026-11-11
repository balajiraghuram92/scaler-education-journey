"""Ported from api/Services/Exercises/IExerciseRepository.cs."""

from __future__ import annotations

from typing import Protocol

from .exercise_manifest_models import ExerciseDefinition


class IExerciseRepository(Protocol):
    def get_by_id(self, exercise_id: str) -> ExerciseDefinition | None:
        ...
