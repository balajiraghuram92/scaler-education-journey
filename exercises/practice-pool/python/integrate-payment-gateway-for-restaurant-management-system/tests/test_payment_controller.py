import unittest
from typing import List

from adapters import PaymentGatewayAdapter
from controllers import PaymentController
from models import Bill, PaymentStatus
from repositories import BillRepository
from services import PaymentService
from dtos import MakePaymentRequestDto, MakePaymentResponseDto, ResponseStatus

class TestPaymentController(unittest.TestCase):

    def get_razorpay_adapter_klass(self):
        subclasses_of_gateway_adapter = PaymentGatewayAdapter.__subclasses__()
        for subclass in subclasses_of_gateway_adapter:
            if subclass.__name__ == "RazorpayAdapter":
                return subclass

        assert False, "RazorpayAdapter need to extend PaymentGatewayAdapter"


    def get_paytm_adapter_klass(self):
        subclasses_of_gateway_adapter = PaymentGatewayAdapter.__subclasses__()
        for subclass in subclasses_of_gateway_adapter:
            if subclass.__name__ == "PaytmAdapter":
                return subclass

        assert False, "PaytmAdapter need to extend PaymentGatewayAdapter"


    def get_payment_service_klass(self):
        subclasses = PaymentService.__subclasses__()
        if len(subclasses) < 1:
            assert False, "No implementation of PaymentService"

        return subclasses[0]


    def get_bill_repository(self):
        subclasses = BillRepository.__subclasses__()
        if len(subclasses) < 1:
            assert False, "No implementation of BillRepository"

        return subclasses[0]()


    def test_make_payment_with_paytm(self):
        gateway_adapter = self.get_paytm_adapter_klass()()
        bill_repository = self.get_bill_repository()
        payment_service = self.get_payment_service_klass()(bill_repository, gateway_adapter)
        payment_controller = PaymentController(payment_service)

        bill = Bill(
            total_amount=100,
            gst=18,
            service_charge=10
        )

        bill = bill_repository.save(bill)

        response = payment_controller.make_payment(
            MakePaymentRequestDto(
                bill_id=bill.id
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS


    def test_make_payment_with_razorpay(self):
        gateway_adapter = self.get_razorpay_adapter_klass()()
        bill_repository = self.get_bill_repository()
        payment_service = self.get_payment_service_klass()(bill_repository, gateway_adapter)
        payment_controller = PaymentController(payment_service)

        bill = Bill(
            total_amount=100,
            gst=18,
            service_charge=10
        )

        bill = bill_repository.save(bill)

        response = payment_controller.make_payment(
            MakePaymentRequestDto(
                bill_id=bill.id
            )
        )

        assert response.response_status == ResponseStatus.SUCCESS
