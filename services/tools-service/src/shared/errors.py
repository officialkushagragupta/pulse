"""Shared kernel: base error types reused across this service's layers.

Generic building blocks live here (not in domain/) so they are not duplicated across
domain/application/infrastructure/api. The api layer maps these onto HTTP responses (T10).
"""


class DomainError(Exception):
    """Base class for all domain errors."""


class EntityNotFound(DomainError):
    """A requested entity does not exist (e.g. unknown employee id)."""
