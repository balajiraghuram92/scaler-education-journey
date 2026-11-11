"""Shared-secret auth, the same idea as the .NET x-api-key check.

Every endpoint except /health and /health/ready requires the ``x-api-key``
header to equal the configured shared secret. Comparison is constant-time;
an empty configured secret fails closed (everything 401s).
"""

import hmac

from fastapi import HTTPException, Request

API_KEY_HEADER = "x-api-key"


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=401, detail="Missing or invalid API key")


async def require_api_key(request: Request) -> None:
    secret: str = request.app.state.settings.api_shared_secret
    provided = request.headers.get(API_KEY_HEADER, "")
    if not secret or not hmac.compare_digest(provided.encode("utf-8"), secret.encode("utf-8")):
        raise _unauthorized()
