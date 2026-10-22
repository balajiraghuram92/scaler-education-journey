from .publisher import Publisher


class TaskManager(Publisher):
    def __init__(self):
        super().__init__()

    def assign_task(self, task_id: int, user_id: int) -> None:
        self.notify_observers(user_id, task_id)
