from abc import ABC, abstractmethod


class Observer(ABC):
    """Observer interface.

    Declare one abstract method: send_notification(self, user_id: int, task_id: int) -> None
    """


class AppService(Observer):
    """In-app channel. Print one line that mentions "App", the task id and the user id."""

    def send_notification(self, user_id: int) -> None:  # old signature: update it
        raise NotImplementedError("Implement the new signature")


class EmailService(Observer):
    """Email channel. Print one line that mentions "Email", the task id and the user id."""

    def send_notification(self, user_id: int) -> None:  # old signature: update it
        raise NotImplementedError("Implement the new signature")


class SlackService(Observer):
    """Slack channel. Print one line that mentions "Slack", the task id and the user id."""

    def send_notification(self, user_id: int) -> None:  # old signature: update it
        raise NotImplementedError("Implement the new signature")
