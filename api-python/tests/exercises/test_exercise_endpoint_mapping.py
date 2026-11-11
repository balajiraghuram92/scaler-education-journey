"""Translated from ExerciseEndpointMappingTests.cs."""

from __future__ import annotations

from app.main import create_app


def _flatten_routes(routes, prefix=""):
    """Yield (full path, route) for every leaf route.

    With fastapi==0.141.1, routes added through include_router sit
    behind mount-like entries in app.routes, so the flat list holds
    only the top-level entries; entries with their own routes list
    are descended into with the parent prefix joined on.
    """
    for route in routes:
        sub_routes = getattr(route, "routes", None)
        if sub_routes:
            parent = getattr(route, "path", "") or getattr(route, "prefix", "")
            yield from _flatten_routes(sub_routes, prefix + parent)
        else:
            yield prefix + getattr(route, "path", ""), route


def test_endpoint_mapping_registers_run_and_check_routes() -> None:
    app = create_app()
    flat = list(_flatten_routes(app.routes))
    routes = {
        (path, name)
        for path, route in flat
        if (name := getattr(route, "name", None))
    }
    methods = {
        getattr(route, "name", ""): set(getattr(route, "methods", set()) or set())
        for _, route in flat
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
