from __future__ import annotations

import dataclasses
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
        return Query.QueryBuilder()

    class QueryBuilder(Builder["Query"]):
        def __init__(self):
            self._instance = Query(None, None, None, None, None, None)

        def select(self, select: str) -> Query.QueryBuilder:
            self._instance.select = select
            return self

        def from_(self, from_: str) -> Query.QueryBuilder:
            self._instance.from_ = from_
            return self

        def where(self, where: str) -> Query.QueryBuilder:
            self._instance.where = where
            return self

        def join(self, join: str) -> Query.QueryBuilder:
            self._instance.join = join
            return self

        def order_by(self, order_by: str) -> Query.QueryBuilder:
            self._instance.order_by = order_by
            return self

        def group_by(self, group_by: str) -> Query.QueryBuilder:
            self._instance.group_by = group_by
            return self

        def build(self) -> Query:
            return dataclasses.replace(self._instance)
