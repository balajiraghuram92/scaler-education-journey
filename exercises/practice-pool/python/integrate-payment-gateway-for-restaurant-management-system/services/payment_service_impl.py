from adapters import PaymentGatewayAdapter
from models import Bill
from repositories import BillRepository
from .payment_service import PaymentService
from exceptions import InvalidBillError


class PaymentServiceImpl(PaymentService):

    def __init__(
            self,
            bill_repository: BillRepository,
            payment_gateway_adaptor: PaymentGatewayAdapter
    ):
        self.bill_repository = bill_repository
        self.payment_gateway_adaptor = payment_gateway_adaptor

    def make_payment(self, bill_id):
        bill: Bill = self.bill_repository.find_by_id(bill_id)

        if bill is None:
            raise InvalidBillError("Bill is not found with id: {}".format(bill_id))

        return self.payment_gateway_adaptor.make_payment(bill_id, bill.total_amount)



