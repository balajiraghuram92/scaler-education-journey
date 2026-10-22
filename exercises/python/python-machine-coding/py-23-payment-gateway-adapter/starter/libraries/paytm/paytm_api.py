from libraries.paytm.paytm_payment_response import PaytmPaymentResponse


class PaytmApi:
    """Stand-in for the third-party Paytm SDK (it names its method make_payment)."""

    def make_payment(self, bill_id: int, amount: float) -> PaytmPaymentResponse:
        return PaytmPaymentResponse(txn_id=f"PAYTM-{bill_id}", payment_status="SUCCESS")
