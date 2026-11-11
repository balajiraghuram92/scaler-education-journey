"""Translated from ExerciseEndpointMappingTests.cs."""

from __future__ import annotations

from app.main import create_app


def test_endpoint_mapping_registers_run_and_check_routes() -> None:
    app = create_app()
    routes = {
        (getattr(route, "path", ""), name)
        for route in app.routes
        if (name := getattr(route, "name", None))
    }
    methods = {
        getattr(route, "name", ""): set(getattr(route, "methods", set()) or set())
        for route in app.routes
    }

    # FastAPI names routes after the handler function; the C# names are noted here.
    assert ("/api/exercises/{exercise_id}", "get_metadata") in routes  # GetExerciseMetadata
    assert ("/api/exercises/{exercise_id}/solution", "get_solution") in routes  # GetExerciseSolution
    assert ("/api/exercises/{exercise_id}/run", "execute_run") in routes  # RunExercise
    assert ("/api/exercises/{exercise_id}/check", "execute_check") in routes  # CheckExercise
    assert (
        "/api/exercises/{exercise_id}/workspace",
        "get_workspace_state",
    ) in routes  # GetExerciseWorkspaceState
    assert ("/api/exercises/{exercise_id}/draft", "save_draft") in routes  # SaveExerciseDraft
    assert methods["execute_run"] == {"POST"}
    assert methods["execute_check"] == {"POST"}
    assert methods["save_draft"] == {"PUT"}
