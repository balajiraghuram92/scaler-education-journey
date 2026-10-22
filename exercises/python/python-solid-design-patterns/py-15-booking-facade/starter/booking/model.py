from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class PaymentStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class BookingStatus(Enum):
    SUCCESS = "SUCCESS"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    PAYMENT_FAILED = "PAYMENT_FAILED"


@dataclass
class BookingConfirmation:
    user_id: str
    accommodation_id: str
    check_in_date: date
    check_out_date: date


@dataclass
class BookingResult:
    status: BookingStatus
    confirmation: Optional[BookingConfirmation] = None
    error_message: Optional[str] = None

    @staticmethod
    def success(confirmation: BookingConfirmation) -> BookingResult:
        return BookingResult(BookingStatus.SUCCESS, confirmation)

    @staticmethod
    def not_available(error_message: str) -> BookingResult:
        return BookingResult(
            BookingStatus.NOT_AVAILABLE, error_message=error_message
        )

    @staticmethod
    def payment_failed(error_message: str) -> BookingResult:
        return BookingResult(
            BookingStatus.PAYMENT_FAILED, error_message=error_message
        )
