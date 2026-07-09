"""SqlExecutor port — runs a guard-validated read-only query and applies a row cap.

The read-only guard (T2) validates the query in the domain BEFORE the use case ever
calls this port, so an adapter here only executes and caps.
"""
from typing import Protocol

from domain.values import QueryResult


class SqlExecutor(Protocol):
    def execute(self, query: str) -> QueryResult: ...
