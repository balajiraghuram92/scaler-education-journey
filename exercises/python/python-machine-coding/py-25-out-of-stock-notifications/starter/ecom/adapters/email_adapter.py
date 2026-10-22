from abc import ABC, abstractmethod


class EmailAdapter(ABC):

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        pass
