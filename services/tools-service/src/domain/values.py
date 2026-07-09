"""Domain value objects — computed/aggregate shapes that are not table rows."""
from dataclasses import dataclass

from domain.entities import Leave


@dataclass(frozen=True, slots=True)
class LeaveBalance:
    """An employee's leave standing across all leave types (hr_get_leave_balance)."""

    employee_id: int
    entries: tuple[Leave, ...]


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Rows returned by the SqlExecutor for sql_run.

    `truncated` is True when the executor's row cap clipped the result set.
    """

    columns: tuple[str, ...]
    rows: tuple[dict[str, object], ...]
    truncated: bool


@dataclass(frozen=True, slots=True)
class RenderedDocument:
    """A generated document (doc_generate): raw bytes plus how to serve them."""

    content: bytes
    media_type: str
    filename: str
