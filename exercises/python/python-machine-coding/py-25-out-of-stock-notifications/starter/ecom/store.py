import threading
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Optional, Type, TypeVar

from ecom.models import Inventory

T = TypeVar("T")


class Store:
    """The in-memory stand-in for the Django ORM: one table per model class, keyed by id.

    add(obj)                    insert (assigns the next id when obj.id == 0) or replace; returns obj
    get(Model, id)              the row or None
    first(Model, **filters)     the first row whose attributes equal the filters (or None)
    find(Model, **filters)      every matching row, in insertion order
    delete(obj)                 remove the row (missing rows are ignored)
    inventory_of(product_id)    the Inventory row of a product, or None
    transaction()               context manager: holds the store-wide lock (so check-then-update
                                sequences are atomic across threads) and rolls every change back,
                                including inserts and deletes, if the block raises
    Rows are ordinary objects: change their attributes directly (there is nothing to save).
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._tables: dict[type, dict[int, Any]] = defaultdict(dict)
        self._next_id: dict[type, int] = defaultdict(lambda: 1)

    def add(self, obj: T) -> T:
        with self._lock:
            table = self._tables[type(obj)]
            if not obj.id:
                obj.id = self._next_id[type(obj)]
                self._next_id[type(obj)] += 1
            table[obj.id] = obj
            return obj

    def get(self, model: Type[T], row_id: int) -> Optional[T]:
        with self._lock:
            return self._tables[model].get(row_id)

    def find(self, model: Type[T], **filters: Any) -> list[T]:
        with self._lock:
            return [row for row in self._tables[model].values()
                    if all(getattr(row, name) == value for name, value in filters.items())]

    def first(self, model: Type[T], **filters: Any) -> Optional[T]:
        rows = self.find(model, **filters)
        return rows[0] if rows else None

    def delete(self, obj: Any) -> None:
        with self._lock:
            self._tables[type(obj)].pop(obj.id, None)

    def inventory_of(self, product_id: int) -> Optional[Inventory]:
        with self._lock:
            for inventory in self._tables[Inventory].values():
                if inventory.product.id == product_id:
                    return inventory
            return None

    @contextmanager
    def transaction(self):
        with self._lock:
            tables = {model: dict(rows) for model, rows in self._tables.items()}
            states = [(row, dict(row.__dict__)) for rows in tables.values() for row in rows.values()]
            counters = dict(self._next_id)
            try:
                yield self
            except BaseException:
                self._tables = defaultdict(dict, {model: dict(rows) for model, rows in tables.items()})
                self._next_id = defaultdict(lambda: 1, counters)
                for row, state in states:
                    row.__dict__.clear()
                    row.__dict__.update(state)
                raise
