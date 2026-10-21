from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Cloneable(ABC, Generic[T]):

    @abstractmethod
    def clone_object(self) -> T:
        pass
