from typing import List

from .observer import Observer
from .registry import ObserverRegistry


class Publisher(ObserverRegistry):
    """Keeps subscribers and notifies them.

    - __init__ creates a per-instance list named ``observers``
    - add_observer appends, remove_observer removes (an unsubscribed observer gets nothing)
    - notify_observers(stock_name, new_price) calls
      observer.send_notification(stock_name, new_price) on every observer, in subscription order
    """

    def __init__(self):
        raise NotImplementedError("Create self.observers")

    def add_observer(self, observer: Observer) -> None:
        raise NotImplementedError("Subscribe the observer")

    def remove_observer(self, observer: Observer) -> None:
        raise NotImplementedError("Unsubscribe the observer")

    def notify_observers(self, stock_name: str, new_price: float) -> None:
        raise NotImplementedError("Notify every observer in order")
