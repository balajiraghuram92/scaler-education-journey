from abc import ABC, abstractmethod

from audit_protocol import Auditable  # noqa: F401
from mixins import LoggingMixin, AuditMixin


class PaymentGateway(ABC):
    """Abstract gateway with self-registration.

    - class-level ``registry = {}``
    - ``__init_subclass__(cls, gateway_name=None, **kwargs)``: call ``super().__init_subclass__(**kwargs)``
      and register the class under ``gateway_name`` when it is given
    - abstract ``process_payment(amount)`` and ``refund(amount)``
    """

    registry = {}

    def __init_subclass__(cls, gateway_name=None, **kwargs):
        # TODO: forward **kwargs to super() and register the subclass under gateway_name
        pass

    @abstractmethod
    def process_payment(self, amount):
        """Charge ``amount``."""

    @abstractmethod
    def refund(self, amount):
        """Return ``amount`` to the customer."""


class PhonePeGateway(PaymentGateway, LoggingMixin, AuditMixin, gateway_name="phonepe"):
    """Registered as ``"phonepe"``. Both methods call ``log_action`` and ``record_audit``:

    - ``process_payment(500)`` logs ``Processing payment of 500`` and audits ``Processed payment of 500``
    - ``refund(200)`` logs a line mentioning ``200`` and audits ``Refunded 200``
    """

    def __init__(self):
        super().__init__()

    def process_payment(self, amount):
        raise NotImplementedError("Implement PhonePeGateway.process_payment")

    def refund(self, amount):
        raise NotImplementedError("Implement PhonePeGateway.refund")


class RazorpayGateway(PaymentGateway, LoggingMixin, AuditMixin, gateway_name="razorpay"):
    """Registered as ``"razorpay"``; same behaviour as the other gateways."""

    def __init__(self):
        super().__init__()

    def process_payment(self, amount):
        raise NotImplementedError("Implement RazorpayGateway.process_payment")

    def refund(self, amount):
        raise NotImplementedError("Implement RazorpayGateway.refund")


class PaytmGateway(PaymentGateway, LoggingMixin, AuditMixin, gateway_name="paytm"):
    """Registered as ``"paytm"``; same behaviour as the other gateways."""

    def __init__(self):
        super().__init__()

    def process_payment(self, amount):
        raise NotImplementedError("Implement PaytmGateway.process_payment")

    def refund(self, amount):
        raise NotImplementedError("Implement PaytmGateway.refund")


def run_audit_check(obj):
    """Return ``isinstance(obj, Auditable)``."""
    raise NotImplementedError("Implement run_audit_check")
