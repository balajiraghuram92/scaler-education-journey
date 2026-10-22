from .observer import *
from .publisher import Publisher


class StockTradingManager(Publisher):
    """The subject: a stock whose price changes.

    __init__(stock_name, initial_price, notification_threshold) calls super().__init__()
    and stores stock_name, current_price (= initial_price) and notification_threshold.

    update_stock_price(new_price) always updates current_price, and notifies the observers
    (with the stock name and the new price) only if new_price is strictly greater than
    notification_threshold.
    """

    def __init__(
        self, stock_name: str, initial_price: float, notification_threshold: float
    ):
        raise NotImplementedError("Initialise the publisher and store the fields")

    def update_stock_price(self, new_price: float) -> None:
        raise NotImplementedError("Update the price and notify above the threshold")
