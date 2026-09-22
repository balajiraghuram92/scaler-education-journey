from abc import ABC, abstractmethod


class PaymentGatewayAdapter(ABC):

    @abstractmethod
    def make_payment(
            self,
            bill_id: int,
            amount: float
    ):
        pass
