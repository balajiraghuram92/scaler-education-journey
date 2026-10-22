import threading
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, FastAPI, Header, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class PaymentIn(BaseModel):
    customer_id: int = Field(gt=0)
    amount_cents: int = Field(gt=0, le=1_000_000)
    currency: Literal["USD", "EUR", "INR"]


class PaymentOut(BaseModel):
    id: UUID
    customer_id: int
    amount_cents: int
    currency: str
    status: Literal["captured"] = "captured"


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


_LOCK = threading.Lock()
_RECORDS: dict[str, tuple[PaymentIn, PaymentOut]] = {}

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_payment(
    body: PaymentIn,
    response: Response,
    idempotency_key: Annotated[str, Header(min_length=8)],
) -> PaymentOut:
    with _LOCK:  # the whole check-then-store step must be atomic
        existing = _RECORDS.get(idempotency_key)
        if existing is None:
            payment = PaymentOut(
                id=uuid4(),
                customer_id=body.customer_id,
                amount_cents=body.amount_cents,
                currency=body.currency,
            )
            _RECORDS[idempotency_key] = (body, payment)
            return payment
        original_body, original_payment = existing
    if original_body != body:
        raise ApiError(
            status.HTTP_409_CONFLICT,
            "idempotency_key_reuse",
            "this Idempotency-Key was already used with a different request body",
        )
    response.status_code = status.HTTP_200_OK
    response.headers["Idempotent-Replayed"] = "true"
    return original_payment


app = FastAPI(title="Payments", version="1.0.0")
app.include_router(router)


def _envelope(code: str, message: str, fields: list[dict[str, str]]) -> dict[str, object]:
    return {"error": {"code": code, "message": message, "fields": fields}}


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=_envelope(exc.code, exc.message, []))


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    fields = [
        {"loc": ".".join(str(part) for part in err["loc"]), "msg": str(err["msg"])}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_envelope("validation_error", "request validation failed", fields),
    )
