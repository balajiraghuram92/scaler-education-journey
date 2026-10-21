from abc import ABC, abstractmethod
from typing import Dict, Optional

from .model import UserIntrinsicState


class FlyweightRegistry(ABC):
    """Interface. Leave unchanged."""

    @abstractmethod
    def add_flyweight(self, flyweight: UserIntrinsicState) -> None:
        pass

    @abstractmethod
    def get_flyweight(self, email: str) -> Optional[UserIntrinsicState]:
        pass


class FlyweightRegistryImpl(FlyweightRegistry):
    """Stores shared flyweights in a dict attribute named ``_flyweights``, keyed by email.

    - add_flyweight stores the object itself (not a copy), keyed by ``flyweight.email``
    - get_flyweight returns that same object, or None when the email is unknown
    - every registry instance has its own storage
    """

    def __init__(self):
        raise NotImplementedError("Create the _flyweights dict")

    def add_flyweight(self, flyweight: UserIntrinsicState) -> None:
        raise NotImplementedError("Store the flyweight by email")

    def get_flyweight(self, email: str) -> Optional[UserIntrinsicState]:
        raise NotImplementedError("Look up the flyweight by email")
