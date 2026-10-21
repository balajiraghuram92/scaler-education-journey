from typing import List

from .observer import Observer
from .registry import ObserverRegistry


class Publisher(ObserverRegistry):
    def __init__(self):
        self.observers: List[Observer] = []

    def add_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def notify_observers(self, user_id: int, task_id: int) -> None:
        for observer in list(self.observers):
            observer.send_notification(user_id, task_id)
