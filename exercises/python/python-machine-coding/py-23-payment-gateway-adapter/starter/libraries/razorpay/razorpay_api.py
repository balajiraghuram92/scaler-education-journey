from libraries.razorpay.razorpay_payment_response import RazorpayPaymentResponse


class RazorpayApi:
    """Stand-in for the third-party Razorpay SDK (it names its method process_payment)."""

    def process_payment(self, bill_id: int, transaction_amount: float) -> RazorpayPaymentResponse:
        return RazorpayPaymentResponse(transaction_id=f"RZP-{bill_id}", payment_status="SUCCESS")
