"""Ported from the Problem(...) helpers and middleware in api/Program.cs.

Produces exactly the application/problem+json body shape the C# emits:
{type, title, status, detail, instance, traceId}.
"""

from __future__ import annotations

from fastapi.responses import JSONResponse


PROBLEM_MEDIA_TYPE = "application/problem+json"


def problem_body(
    *,
    status: int,
    title: str,
    detail: str = "",
    instance: str = "",
    trace_id: str = "",
    type_url: str = "",
) -> dict[str, object]:
    return {
        "type": type_url or f"https://httpstatuses.com/{status}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
        "traceId": trace_id,
    }


def problem_response(
    *,
    status: int,
    title: str,
    detail: str = "",
    instance: str = "",
    trace_id: str = "",
    type_url: str = "",
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content=problem_body(
            status=status,
            title=title,
            detail=detail,
            instance=instance,
            trace_id=trace_id,
            type_url=type_url,
        ),
        media_type=PROBLEM_MEDIA_TYPE,
    )


class ApiProblem(Exception):
    """Raised by services/routers to return a problem-details response."""

    def __init__(
        self,
        status: int,
        title: str,
        detail: str = "",
        instance: str = "",
        type_url: str = "",
    ) -> None:
        super().__init__(detail or title)
        self.status = status
        self.title = title
        self.detail = detail
        self.instance = instance
        self.type_url = type_url


class NotFoundProblem(ApiProblem):
    def __init__(self, detail: str = "Not found.", instance: str = "") -> None:
        super().__init__(404, "Not Found", detail, instance)


class BadRequestProblem(ApiProblem):
    def __init__(self, detail: str = "Bad request.", instance: str = "") -> None:
        super().__init__(400, "Bad Request", detail, instance)


class UnauthorizedProblem(ApiProblem):
    def __init__(self, detail: str = "Unauthorized.", instance: str = "") -> None:
        super().__init__(401, "Unauthorized", detail, instance)


class ForbiddenProblem(ApiProblem):
    def __init__(self, detail: str = "Forbidden.", instance: str = "") -> None:
        super().__init__(403, "Forbidden", detail, instance)


class ConflictProblem(ApiProblem):
    def __init__(self, detail: str = "Conflict.", instance: str = "") -> None:
        super().__init__(409, "Conflict", detail, instance)


class TooManyRequestsProblem(ApiProblem):
    def __init__(self, detail: str = "Too many requests.", instance: str = "") -> None:
        super().__init__(429, "Too Many Requests", detail, instance)


def endpoint_problem(request: object, status: int, title: str, detail: str) -> JSONResponse:
    """The per-endpoint-file `Problem(...)` helper (Auth/AdminEndpoints.cs).

    Uses the fixed type URL those files use rather than the generic default.
    """
    path = str(getattr(getattr(request, "url", None), "path", "") or "")
    trace_id = str(getattr(getattr(request, "state", None), "correlation_id", "") or "")
    return problem_response(
        status=status,
        title=title,
        detail=detail,
        instance=path,
        trace_id=trace_id,
        type_url="https://tools.ietf.org/html/rfc7231",
    )
