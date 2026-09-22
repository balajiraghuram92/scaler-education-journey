from abc import ABC, abstractmethod
from typing import List

from scaler.models import Communication


class CommunicationService(ABC):

    @abstractmethod
    def broadcast_message(
            self,
            batch_id: int,
            sender_id: int,
            message: str
    ) -> Communication:
        pass
