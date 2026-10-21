from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Charge:
    gateway: str
    amount: Decimal
    currency: str
    customer_id: str


class PaymentGateway(Protocol):
    def charge(self, amount: Decimal, currency: str, customer_id: str) -> Charge: ...


class ConfigurationError(Exception):
    """The routing table references a gateway that was not provided."""


class CheckoutService:
    """Routes each payment to a gateway chosen by the customer's country.

    - ``gateways`` maps a gateway name to a PaymentGateway; ``routes`` maps an
      ISO country code to a gateway name (lookups are case-insensitive);
      ``default`` is the gateway name used for countries without a route.
    - Fail fast with ConfigurationError if ``default`` or any routed name is
      missing from ``gateways``.
    - Take defensive copies of the mappings.
    - Never import or name a concrete gateway.
    """

    def __init__(
        self,
        gateways: Mapping[str, PaymentGateway],
        routes: Mapping[str, str],
        default: str,
    ) -> None:
        raise NotImplementedError("Implement the constructor")

    def gateway_for(self, country: str) -> str:
        """Return the name of the gateway that handles ``country``."""
        raise NotImplementedError("Implement gateway_for")

    def checkout(self, country: str, amount: Decimal, currency: str, customer_id: str) -> Charge:
        """Delegate to the chosen gateway; ValueError (no gateway call) if amount <= 0."""
        raise NotImplementedError("Implement checkout")
