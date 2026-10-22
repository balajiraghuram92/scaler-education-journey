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
V = TypeVar('V', bound=VersionedModel)

class VersionedRepository(Generic[V]):
    """In-memory repository with optimistic concurrency.

    It stores and returns copies, so a caller can never mutate stored state without calling save(),
    and a save whose version no longer matches is rejected instead of silently overwriting.
    """

    def __init__(self, clock: Callable[[], datetime]=datetime.now) -> None:
        """Keep a dict of stored entities, an id counter starting at 1, the injected clock and a threading.Lock."""
        raise NotImplementedError('TODO: implement __init__')

    def save(self, item: V) -> V:
        """Under the lock: first save (id is None) assigns the next id and created_at; otherwise raise UnknownEntityError for an unknown id and StaleWriteError when stored.version != item.version. Then increment item.version, set last_modified_at from the clock, store a copy.copy of the item and return the item."""
        raise NotImplementedError('TODO: implement save')

    def find_by_id(self, item_id: int) -> V | None:
        """Under the lock return a copy of the stored entity, or None."""
        raise NotImplementedError('TODO: implement find_by_id')
