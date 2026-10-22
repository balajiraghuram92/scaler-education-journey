from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from ecom.models import Inventory, Order


class ResponseStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class PlaceOrderReqDto:
    user_id: int
    product_ids_with_quantity: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class PlaceOrderResDto:
    order: Optional[Order] = None
    response_status: Optional[ResponseStatus] = None


@dataclass
class CancelOrderReqDto:
    user_id: int
    order_id: int


@dataclass
class CancelOrderResDto:
    order: Optional[Order] = None
    response_status: Optional[ResponseStatus] = None


@dataclass
class CreateUpdateInventoryReqDto:
    user_id: int = 0
    product_id: int = 0
    quantity: int = 0


@dataclass
class CreateUpdateInventoryResponseDto:
    inventory: Optional[Inventory] = None
    response_status: Optional[ResponseStatus] = None


CreateUpdateInventoryResDto = CreateUpdateInventoryResponseDto


@dataclass
class DeleteInventoryReqDto:
    user_id: int
    product_id: int


@dataclass
class DeleteInventoryResponseDto:
    response_status: Optional[ResponseStatus] = None


@dataclass
class DeliveryEstimateReqDto:
    product_id: int
    address_id: int


@dataclass
class DeliveryEstimateResDto:
    expected_delivery: Optional[datetime] = None
    response_status: Optional[ResponseStatus] = None


@dataclass
class RegisterUserNotifyReqDto:
    user_id: int
    product_id: int


@dataclass
class RegisterUserNotifyResDto:
    response_status: Optional[ResponseStatus] = None
    notification_id: Optional[int] = None


UnregisterUserNotifyReqDto = RegisterUserNotifyReqDto
UnregisterUserNotifyResDto = RegisterUserNotifyResDto
