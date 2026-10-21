from abc import ABC, abstractmethod


class Observer(ABC):
    """Observer interface.

    Declare one abstract method:
    send_notification(self, stock_name: str, current_price: float) -> None
    """


class AppService(Observer):
    """In-app channel. Print one line that mentions "App", the stock name and the price."""

    def send_notification(self, stock_name: str) -> None:  # old signature: update it
        raise NotImplementedError("Implement the new signature")


class EmailService(Observer):
    """Email channel. Print one line that mentions "Email", the stock name and the price."""

    def send_notification(self, stock_name: str) -> None:  # old signature: update it
        raise NotImplementedError("Implement the new signature")


class SmsService(Observer):
    """SMS channel. Print one line that mentions "SMS", the stock name and the price."""

    def send_notification(self, stock_name: str) -> None:  # old signature: update it
        raise NotImplementedError("Implement the new signature")
