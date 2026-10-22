from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def send_notification(self, stock_name: str, current_price: float) -> None:
        pass

class AppService(Observer):
    def send_notification(self, stock_name: str, current_price: float) -> None:
        subject = "Price update for " + stock_name
        message = "New price is " + str(current_price)
        print(f"App notification: {subject} - {message}")


class EmailService(Observer):
    def send_notification(self, stock_name: str, current_price: float) -> None:
        subject = "Price update for " + stock_name
        message = "New price is " + str(current_price)
        print(f"Email notification: {subject} - {message}")


class SmsService(Observer):
    def send_notification(self, stock_name: str, current_price: float) -> None:
        subject = "Price update for " + stock_name
        message = "New price is " + str(current_price)
        print(f"SMS notification: {subject} - {message}")
