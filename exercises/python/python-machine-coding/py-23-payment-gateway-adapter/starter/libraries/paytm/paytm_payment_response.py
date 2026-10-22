class PaytmPaymentResponse:
    """What the Paytm SDK returns: a transaction id and a plain string status."""

    def __init__(self, txn_id: str, payment_status: str):
        self.txn_id = txn_id
        self.payment_status = payment_status
