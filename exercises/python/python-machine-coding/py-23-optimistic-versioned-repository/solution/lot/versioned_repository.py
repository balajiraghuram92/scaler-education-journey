import copy
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from lot.models import BaseModel


class StaleWriteError(Exception):
    """The stored entity changed since the caller read it."""


class UnknownEntityError(Exception):
    """save() was called for an id the repository has never issued."""


@dataclass(kw_only=True, eq=False)
class VersionedModel(BaseModel):
    version: int = 0


V = TypeVar("V", bound=VersionedModel)


class VersionedRepository(Generic[V]):
    """In-memory repository with optimistic concurrency.

    It stores and returns copies, so a caller can never mutate stored state without calling save(),
    and a save whose version no longer matches is rejected instead of silently overwriting.
    """

    def __init__(self, clock: Callable[[], datetime] = datetime.now) -> None:
        self._items: dict[int, V] = {}
        self._next_id = 1
        self._clock = clock
        self._lock = threading.Lock()

    def save(self, item: V) -> V:
        with self._lock:
            now = self._clock()
            if item.id is None:
                item.id = self._next_id
                self._next_id += 1
                item.created_at = now
            else:
                stored = self._items.get(item.id)
                if stored is None:
                    raise UnknownEntityError(item.id)
                if stored.version != item.version:
                    raise StaleWriteError(f"entity {item.id}: expected version {stored.version}, got {item.version}")
            item.version += 1
            item.last_modified_at = now
            self._items[item.id] = copy.copy(item)
            return item

    def find_by_id(self, item_id: int) -> V | None:
        with self._lock:
            stored = self._items.get(item_id)
            return copy.copy(stored) if stored is not None else None
