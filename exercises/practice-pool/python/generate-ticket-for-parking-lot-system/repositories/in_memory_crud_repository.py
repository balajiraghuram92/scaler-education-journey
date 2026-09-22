from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from typing import TypeVar, Generic

T = TypeVar('T')


class InMemoryCRUDRepository(Generic[T]):
    _data: Dict[int, T]

    def __init__(self):
        self._data = {}
        self.counter = 1

    def find_by_id(self, pk: int) -> Optional[T]:
        return self._data.get(pk, None)

    def update(self, obj: T, pk: int) -> T:
        self._data[pk] = obj
        return obj

    def delete(self, pk: int) -> Optional[T]:
        return self._data.pop(pk, None)

    def create(self, obj: T) -> T:
        obj.id = self.counter
        self._data[self.counter] = obj
        self.counter += 1
        return obj

    def find(self, **kwargs) -> List[T]:
        result = []
        for obj in self._data.values():
            match = True
            for key, value in kwargs.items():
                if getattr(obj, key) != value:
                    match = False
                    break
            if match:
                result.append(obj)

        return result

    def find_one(self, **kwargs) -> Optional[T]:
        result = self.find(**kwargs)
        if result:
            return result[0]
        return None
