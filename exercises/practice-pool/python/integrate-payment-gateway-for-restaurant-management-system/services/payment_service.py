from abc import ABC, abstractmethod

from adapters import PaymentGatewayAdapter
from repositories import BillRepository


class PaymentService(ABC):
    bill_repository: BillRepository
    payment_gateway_adaptor: PaymentGatewayAdapter

    @abstractmethod
    def make_payment(self, bill_id):
        pass
