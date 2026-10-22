from abc import ABC, abstractmethod

from audit_protocol import Auditable
from mixins import LoggingMixin, AuditMixin


class PaymentGateway(ABC):
    registry = {}

    def __init_subclass__(cls, gateway_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if gateway_name is not None:
            cls.registry[gateway_name] = cls

    @abstractmethod
    def process_payment(self, amount):
        pass

    @abstractmethod
    def refund(self, amount):
        pass


class PhonePeGateway(PaymentGateway, LoggingMixin, AuditMixin, gateway_name="phonepe"):
    def __init__(self):
        super().__init__()

    def process_payment(self, amount):
        self.log_action(f"Processing payment of {amount}")
        self.record_audit(f"Processed payment of {amount}")

    def refund(self, amount):
        self.log_action(f"Refunding {amount}")
        self.record_audit(f"Refunded {amount}")


class RazorpayGateway(PaymentGateway, LoggingMixin, AuditMixin, gateway_name="razorpay"):
    def __init__(self):
        super().__init__()

    def process_payment(self, amount):
        self.log_action(f"Processing payment of {amount}")
        self.record_audit(f"Processed payment of {amount}")

    def refund(self, amount):
        self.log_action(f"Refunding {amount}")
        self.record_audit(f"Refunded {amount}")


class PaytmGateway(PaymentGateway, LoggingMixin, AuditMixin, gateway_name="paytm"):
    def __init__(self):
        super().__init__()

    def process_payment(self, amount):
        self.log_action(f"Processing payment of {amount}")
        self.record_audit(f"Processed payment of {amount}")

    def refund(self, amount):
        self.log_action(f"Refunding {amount}")
        self.record_audit(f"Refunded {amount}")


def run_audit_check(obj):
    return isinstance(obj, Auditable)
