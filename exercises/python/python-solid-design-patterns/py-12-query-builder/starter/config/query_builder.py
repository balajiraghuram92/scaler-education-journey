from __future__ import annotations

from dataclasses import dataclass

from .builder import Builder


@dataclass
class Query:
    select: str
    from_: str
    where: str
    join: str
    order_by: str
    group_by: str

    @staticmethod
    def builder() -> QueryBuilder:
        """Return a NEW QueryBuilder on every call."""
        raise NotImplementedError("Implement Query.builder")

    class QueryBuilder(Builder["Query"]):
        """Fluent builder: every setter stores its clause and returns the builder.

        Keep the working state in ``self._instance`` (a Query with every field
        ``None``). ``build()`` returns a configured Query that is independent of the
        builder: later setter calls must not change an object already built.
        """

        def __init__(self):
            raise NotImplementedError("Implement the constructor")

        def select(self, select: str) -> Query.QueryBuilder:
            raise NotImplementedError("Implement select")

        def from_(self, from_: str) -> Query.QueryBuilder:
            raise NotImplementedError("Implement from_")

        def where(self, where: str) -> Query.QueryBuilder:
            raise NotImplementedError("Implement where")

        def join(self, join: str) -> Query.QueryBuilder:
            raise NotImplementedError("Implement join")

        def order_by(self, order_by: str) -> Query.QueryBuilder:
            raise NotImplementedError("Implement order_by")

        def group_by(self, group_by: str) -> Query.QueryBuilder:
            raise NotImplementedError("Implement group_by")

        def build(self) -> Query:
            raise NotImplementedError("Implement build")
