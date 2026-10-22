from .publisher import Publisher


class TaskManager(Publisher):
    """The subject. Call super().__init__() in __init__.

    assign_task(task_id, user_id) notifies every observer with (user_id, task_id).
    Mind the argument order: the manager takes the task first, observers get the user first.
    """

    def __init__(self):
        raise NotImplementedError("Initialise the publisher")

    def assign_task(self, task_id: int, user_id: int) -> None:
        raise NotImplementedError("Notify observers about the assignment")
