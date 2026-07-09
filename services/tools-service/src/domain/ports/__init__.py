"""Domain ports (interfaces/Protocols). Adapters live in infrastructure/."""
from domain.ports.document_renderer import DocumentRenderer
from domain.ports.repositories import (
    EngineeringRepository,
    HrRepository,
    ItRepository,
)
from domain.ports.sql_executor import SqlExecutor

__all__ = [
    "HrRepository",
    "ItRepository",
    "EngineeringRepository",
    "SqlExecutor",
    "DocumentRenderer",
]
