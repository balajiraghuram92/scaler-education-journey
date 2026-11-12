"""Translated from ExerciseEndpointMappingTests.cs."""

from __future__ import annotations

from app.main import create_app


def _flatten_routes(routes, prefix=""):
    """Yield (full path, route) for every leaf route.

    With fastapi==0.141.1, include_router adds _IncludedRouter
    entries to app.routes: the child routes live at
    entry.original_router.routes and the include-time prefix at
    entry.include_context.prefix (the router's own prefix is
    already part of each child path). Plain entries with their
    own routes list are descended into with their path joined on.
    """
    for route in routes:
        orig = getattr(route, "original_router", None)
        if orig is not None:
            yield from _flatten_routes(
                orig.routes, prefix + route.include_context.prefix
            )
        elif getattr(route, "routes", None):
            yield from _flatten_routes(
                route.routes, prefix + getattr(route, "path", "")
            )
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


def test_endpoint_mapping_localization_rebuild_routes() -> None:
    # R6: the jobs, vendor-jobs and ops routes replaced the marketplace and
    # bid routes; every old route name and path segment is gone.
    app = create_app()
    flat = list(_flatten_routes(app.routes))
    routes = {
        (path, name)
        for path, route in flat
        if (name := getattr(route, "name", None))
    }

    assert ("/api/localization/projects/{slug}/jobs", "get_jobs") in routes
    assert (
        "/api/localization/projects/{slug}/jobs/{locale_code}",
        "create_job",
    ) in routes
    assert ("/api/localization/jobs/{job_id:int}/approve", "approve_job") in routes
    assert ("/api/localization/jobs/{job_id:int}/send-back", "send_back_job") in routes
    assert (
        "/api/localization/projects/{slug}/agreement",
        "get_agreement",
    ) in routes
    assert ("/api/localization/vendor/{vendor_id:int}/jobs", "get_jobs") in routes
    assert ("/api/localization/ops/usage", "get_usage_summary") in routes
    assert ("/api/localization/ops/usage/events", "get_usage_events") in routes
    assert ("/api/localization/ops/rates", "get_rates") in routes
    assert ("/api/localization/ops/rates", "add_rate") in routes
    assert (
        "/api/localization/ops/projects/{slug}/controls",
        "get_controls",
    ) in routes
    assert (
        "/api/localization/ops/projects/{slug}/controls",
        "update_controls",
    ) in routes
    assert ("/api/localization/ops/teams", "get_teams") in routes
    assert (
        "/api/localization/ops/projects/{slug}/agreement",
        "get_ops_agreement",
    ) in routes
    assert (
        "/api/localization/ops/projects/{slug}/agreement",
        "save_ops_agreement",
    ) in routes

    assert not any(
        "/marketplace" in path or path.endswith("/bids") for path, _ in routes
    )
    gone = {
        "get_overview",
        "post_to_marketplace",
        "get_bids",
        "award_bid",
        "approve_submission",
        "send_back_for_revision",
        "submit_bid",
        "get_open_jobs",
        "get_awarded_jobs",
    }
    assert gone.isdisjoint(name for _, name in routes)
