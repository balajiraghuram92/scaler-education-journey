class RazorpayPaymentResponse:
    """What the Razorpay SDK returns: it calls the id transaction_id."""

    def __init__(self, transaction_id: str, payment_status: str):
        self.transaction_id = transaction_id
        self.payment_status = payment_status
