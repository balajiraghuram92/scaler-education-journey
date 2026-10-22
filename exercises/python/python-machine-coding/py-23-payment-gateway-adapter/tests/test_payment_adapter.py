import pytest

from adapters.payment_gateway_adapter import PaymentGatewayAdapter
from adapters.paytm_payment_gateway_adapter import PaytmPaymentGatewayAdapter
from adapters.razorpay_payment_gateway_adapter import RazorpayPaymentGatewayAdapter
from controllers.payment_controller import PaymentController
from dtos.make_payment_request_dto import MakePaymentRequestDto
from dtos.response_status import ResponseStatus
from exceptions.invalid_bill_exception import InvalidBillException
from libraries.paytm.paytm_api import PaytmApi
from libraries.paytm.paytm_payment_response import PaytmPaymentResponse
from libraries.razorpay.razorpay_api import RazorpayApi
from libraries.razorpay.razorpay_payment_response import RazorpayPaymentResponse
from models.bill import Bill
from models.payment import Payment
from models.payment_status import PaymentStatus
from repositories.bill_repository_impl import BillRepositoryImpl
from services.payment_service_impl import PaymentServiceImpl


@pytest.fixture
def sdk(monkeypatch):
    """Replace both SDK calls with recorders; set sdk.paytm_status / sdk.razorpay_status to change replies."""

    class State:
        calls = []
        paytm_status = "SUCCESS"
        razorpay_status = "SUCCESS"

    def paytm(self, bill_id, amount):
        State.calls.append(("paytm", bill_id, amount))
        return PaytmPaymentResponse("T-1", State.paytm_status)

    def razorpay(self, bill_id, transaction_amount):
        State.calls.append(("razorpay", bill_id, transaction_amount))
        return RazorpayPaymentResponse("R-1", State.razorpay_status)

    State.calls = []
    State.paytm_status = State.razorpay_status = "SUCCESS"
    monkeypatch.setattr(PaytmApi, "make_payment", paytm)
    monkeypatch.setattr(RazorpayApi, "process_payment", razorpay)
    return State


class FakeAdapter(PaymentGatewayAdapter):
    def __init__(self):
        self.calls = []

    def make_payment(self, bill_id, amount):
        self.calls.append((bill_id, amount))
        return Payment("fake-txn", PaymentStatus.SUCCESS, bill_id)


def repo_with_bill(total=1000.0, gst=180.0, service=100.0):
    repo = BillRepositoryImpl()
    bill = repo.save(Bill(total, gst, service))
    return repo, bill


def test_paytm_adapter_maps_response(sdk):
    payment = PaytmPaymentGatewayAdapter().make_payment(5, 250.0)
    assert isinstance(payment, Payment)
    assert (payment.txn_id, payment.payment_status, payment.bill_id) == ("T-1", PaymentStatus.SUCCESS, 5)
    assert sdk.calls == [("paytm", 5, 250.0)]


def test_razorpay_adapter_maps_response(sdk):
    payment = RazorpayPaymentGatewayAdapter().make_payment(6, 99.5)
    assert (payment.txn_id, payment.payment_status, payment.bill_id) == ("R-1", PaymentStatus.SUCCESS, 6)
    assert sdk.calls == [("razorpay", 6, 99.5)], "Razorpay is called through process_payment"


def test_failure_status_is_mapped_to_enum(sdk):
    sdk.paytm_status = sdk.razorpay_status = "FAILURE"
    assert PaytmPaymentGatewayAdapter().make_payment(1, 1.0).payment_status is PaymentStatus.FAILURE
    assert RazorpayPaymentGatewayAdapter().make_payment(1, 1.0).payment_status is PaymentStatus.FAILURE


def test_adapters_implement_the_interface():
    assert issubclass(PaytmPaymentGatewayAdapter, PaymentGatewayAdapter)
    assert issubclass(RazorpayPaymentGatewayAdapter, PaymentGatewayAdapter)
    with pytest.raises(TypeError):
        PaymentGatewayAdapter()


def test_service_rejects_invalid_bill_without_charging():
    repo, _ = repo_with_bill()
    adapter = FakeAdapter()
    service = PaymentServiceImpl(repo, adapter)
    with pytest.raises(InvalidBillException, match="Invalid bill id"):
        service.make_payment(999)
    assert adapter.calls == []


def test_service_charges_total_plus_gst_plus_service_charge():
    repo, bill = repo_with_bill(1000.0, 180.0, 100.0)
    adapter = FakeAdapter()
    payment = PaymentServiceImpl(repo, adapter).make_payment(bill.id)
    assert adapter.calls == [(bill.id, 1280.0)]
    assert payment.txn_id == "fake-txn"


def test_gateway_is_a_one_line_wiring_change(sdk):
    repo, bill = repo_with_bill()
    via_paytm = PaymentServiceImpl(repo, PaytmPaymentGatewayAdapter()).make_payment(bill.id)
    via_razorpay = PaymentServiceImpl(repo, RazorpayPaymentGatewayAdapter()).make_payment(bill.id)
    assert (via_paytm.txn_id, via_razorpay.txn_id) == ("T-1", "R-1")
    assert [c[0] for c in sdk.calls] == ["paytm", "razorpay"]
    assert all(c[2] == 1280.0 for c in sdk.calls)


def test_controller_success_response():
    repo, bill = repo_with_bill()
    controller = PaymentController(PaymentServiceImpl(repo, FakeAdapter()))
    response = controller.make_payment(MakePaymentRequestDto(bill.id))
    assert response.response_status is ResponseStatus.SUCCESS
    assert response.txn_id == "fake-txn"
    assert response.payment_status is PaymentStatus.SUCCESS


def test_controller_invalid_bill_response():
    repo, _ = repo_with_bill()
    controller = PaymentController(PaymentServiceImpl(repo, FakeAdapter()))
    response = controller.make_payment(MakePaymentRequestDto(404))
    assert response.response_status is ResponseStatus.FAILURE
    assert response.txn_id is None and response.payment_status is None


def test_controller_only_catches_invalid_bill():
    class Boom:
        def make_payment(self, bill_id):
            raise RuntimeError("gateway down")

    with pytest.raises(RuntimeError):
        PaymentController(Boom()).make_payment(MakePaymentRequestDto(1))
