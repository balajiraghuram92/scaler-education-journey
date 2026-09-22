from dataclasses import dataclass, field
from enum import Enum
from ecom.models import GiftCard
from typing import Optional


class ResponseStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class CreateGiftCardRequestDto:
    amount: float


@dataclass
class CreateGiftCardResponseDto:
    response_status: ResponseStatus
    gift_card: Optional[GiftCard] = field(default=None)


@dataclass
class RedeemGiftCardRequestDto:
    gift_card_code: str
    amount: float


@dataclass
class RedeemGiftCardResponseDto:
    response_status: ResponseStatus
    gift_card: Optional[GiftCard] = field(default=None)
