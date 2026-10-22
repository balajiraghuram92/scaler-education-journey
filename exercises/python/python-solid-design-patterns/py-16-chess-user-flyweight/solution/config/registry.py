from abc import ABC, abstractmethod
from typing import Dict, Optional

from .model import UserIntrinsicState


class FlyweightRegistry(ABC):

    @abstractmethod
    def add_flyweight(self, flyweight: UserIntrinsicState) -> None:
        pass

    @abstractmethod
    def get_flyweight(self, email: str) -> Optional[UserIntrinsicState]:
        pass


class FlyweightRegistryImpl(FlyweightRegistry):
    def __init__(self):
        self._flyweights: Dict[str, UserIntrinsicState] = {}

    def add_flyweight(self, flyweight: UserIntrinsicState) -> None:
        self._flyweights[flyweight.email] = flyweight

    def get_flyweight(self, email: str) -> Optional[UserIntrinsicState]:
        return self._flyweights.get(email)
