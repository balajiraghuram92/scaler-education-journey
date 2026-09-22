from abc import ABC, abstractmethod


class EmailService(ABC):

    @abstractmethod
    def notify_user(
            self,
            user: int,
            product: int
    ) -> bool:
        pass


