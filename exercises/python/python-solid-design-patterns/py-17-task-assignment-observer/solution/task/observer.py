from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def send_notification(self, user_id: int, task_id: int) -> None:
        pass


class AppService(Observer):
    def send_notification(self, user_id: int, task_id: int) -> None:
        subject = "New task assigned"
        message = f"Task {task_id} is assigned to user {user_id}"
        print(f"App notification: {subject} - {message}")


class EmailService(Observer):
    def send_notification(self, user_id: int, task_id: int) -> None:
        subject = "New task assigned"
        message = f"Task {task_id} is assigned to user {user_id}"
        print(f"Email notification: {subject} - {message}")


class SlackService(Observer):
    def send_notification(self, user_id: int, task_id: int) -> None:
        subject = "New task assigned"
        message = f"Task {task_id} is assigned to user {user_id}"
        print(f"Slack notification: {subject} - {message}")
