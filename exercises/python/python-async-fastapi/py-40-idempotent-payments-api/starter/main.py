import threading
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, FastAPI, Header, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class PaymentIn(BaseModel):
    """Request body. Add: customer_id (int > 0), amount_cents (int, > 0 and <= 1_000_000),
    currency (Literal["USD", "EUR", "INR"])."""


class PaymentOut(BaseModel):
    """Response body. Add: id (UUID), customer_id, amount_cents, currency,
    status (always "captured")."""


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


_LOCK = threading.Lock()
_RECORDS: dict[str, tuple[PaymentIn, PaymentOut]] = {}  # idempotency key -> (request, response)

router = APIRouter(prefix="/payments", tags=["payments"])

# TODO: POST "" with status 201. It is a plain ``def`` (runs in the threadpool), so protect the
# check-then-store sequence with ``_LOCK``.
#   - header: ``idempotency_key: Annotated[str, Header(min_length=8)]``
#   - first request with a key: 201 with the new payment; store (body, payment) in _RECORDS
#   - same key + identical body: 200, the stored payment, response header ``Idempotent-Replayed: true``
#   - same key + different body: raise ApiError(409, "idempotency_key_reuse", "...")

app = FastAPI(title="Payments", version="1.0.0")
app.include_router(router)

# TODO: register exception handlers that produce the envelope
#   {"error": {"code": str, "message": str, "fields": list}}
#   - ApiError -> its own status code, its code and message, fields []
#   - RequestValidationError -> 422, code "validation_error",
#     fields = [{"loc": "<dotted path>", "msg": str}, ...]
