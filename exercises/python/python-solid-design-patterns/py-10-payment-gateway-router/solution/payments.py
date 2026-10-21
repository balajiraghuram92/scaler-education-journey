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
    def __init__(
        self,
        gateways: Mapping[str, PaymentGateway],
        routes: Mapping[str, str],
        default: str,
    ) -> None:
        self._gateways = dict(gateways)
        self._routes = {country.upper(): name for country, name in routes.items()}
        self._default = default
        unknown = ({default} | set(self._routes.values())) - self._gateways.keys()
        if unknown:
            raise ConfigurationError(f"unknown gateways: {sorted(unknown)}")

    def gateway_for(self, country: str) -> str:
        return self._routes.get(country.upper(), self._default)

    def checkout(self, country: str, amount: Decimal, currency: str, customer_id: str) -> Charge:
        if amount <= 0:
            raise ValueError("amount must be positive")
        gateway = self._gateways[self.gateway_for(country)]
        return gateway.charge(amount, currency, customer_id)
