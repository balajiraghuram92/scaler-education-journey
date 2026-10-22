from abc import ABC, abstractmethod
from typing import Dict, Optional

from .model import GraphicIntrinsicState, GraphicType


class FlyweightRegistry(ABC):
    """Interface. Leave unchanged."""

    @abstractmethod
    def add_flyweight(self, flyweight: GraphicIntrinsicState) -> None:
        pass

    @abstractmethod
    def get_flyweight(self, type_: GraphicType) -> Optional[GraphicIntrinsicState]:
        pass


class FlyweightRegistryImpl(FlyweightRegistry):
    """Stores shared flyweights in a dict attribute named ``_flyweights``, keyed by graphic type.

    - add_flyweight stores the object itself (not a copy), keyed by ``flyweight.type``
    - get_flyweight returns that same object, or None when the type is unknown
    - every registry instance has its own storage
    """

    def __init__(self):
        raise NotImplementedError("Create the _flyweights dict")

    def add_flyweight(self, flyweight: GraphicIntrinsicState) -> None:
        raise NotImplementedError("Store the flyweight by its type")

    def get_flyweight(self, type_: GraphicType) -> Optional[GraphicIntrinsicState]:
        raise NotImplementedError("Look up the flyweight by type")
