from typing import List

from .observer import Observer
from .registry import ObserverRegistry


class Publisher(ObserverRegistry):
    """Keeps subscribers and notifies them.

    - __init__ creates a per-instance list named ``observers``
    - add_observer appends, remove_observer removes
    - notify_observers(user_id, task_id) calls observer.send_notification(user_id, task_id)
      on every observer, in subscription order
    """

    def __init__(self):
        raise NotImplementedError("Create self.observers")

    def add_observer(self, observer: Observer) -> None:
        raise NotImplementedError("Subscribe the observer")

    def remove_observer(self, observer: Observer) -> None:
        raise NotImplementedError("Unsubscribe the observer")

    def notify_observers(self, user_id: int, task_id: int) -> None:
        raise NotImplementedError("Notify every observer in order")
