from abc import ABC, abstractmethod
from typing import List, Optional

from models.gate import Gate


class GateRepository(ABC):
    @abstractmethod
    def find_by_id(self, gate_id: int) -> Optional[Gate]:
        pass

    @abstractmethod
    def save(self, gate: Gate) -> Gate:
        pass
