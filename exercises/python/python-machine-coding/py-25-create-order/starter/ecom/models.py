from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class UserType(Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


class OrderStatus(Enum):
    PLACED = "PLACED"
    CANCELLED = "CANCELLED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"


class NotificationStatus(Enum):
    PENDING = "PENDING"
    SENT = "SENT"


# eq=False keeps identity comparison and hashability: two rows are the same row only if they are the same object.
@dataclass(eq=False)
class User:
    name: str
    email: str = ""
    user_type: UserType = UserType.CUSTOMER
    id: int = 0


@dataclass(eq=False)
class Seller:
    name: str
    id: int = 0


@dataclass(eq=False)
class Product:
    name: str
    seller: Optional[Seller] = None
    id: int = 0


@dataclass(eq=False)
class Inventory:
    product: Product
    quantity: int = 0
    id: int = 0


@dataclass(eq=False)
class Order:
    user: User
    order_status: OrderStatus = OrderStatus.PLACED
    id: int = 0


@dataclass(eq=False)
class OrderItem:
    order: Order
    product: Product
    quantity: int
    id: int = 0


@dataclass(eq=False)
class UserAddress:
    user: User
    zipcode: str
    latitude: float
    longitude: float
    id: int = 0


@dataclass(eq=False)
class SellerAddress:
    seller: Seller
    latitude: float
    longitude: float
    id: int = 0


@dataclass(eq=False)
class DeliveryHubAddress:
    zipcode: str
    latitude: float
    longitude: float
    id: int = 0


@dataclass(eq=False)
class Notification:
    user: User
    product: Product
    status: NotificationStatus = NotificationStatus.PENDING
    id: int = 0
