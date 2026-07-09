"""Aggregate-oriented repository ports (one per domain aggregate).

Implemented by adapters in infrastructure/ and injected by the composition root. Grouped
by domain aggregate rather than per-table to keep the port surface small.
"""
from typing import Protocol

from domain.entities import Asset, Employee, Incident, JiraTicket, Leave
from domain.enums import AssetType


class HrRepository(Protocol):
    def get_employee(self, employee_id: int) -> Employee | None: ...

    def find_employee(self, name_or_id: str) -> Employee | None: ...

    def list_leaves(self, employee_id: int) -> tuple[Leave, ...]: ...


class ItRepository(Protocol):
    def get_asset(self, employee_id: int, asset_type: AssetType) -> Asset | None: ...

    def add_asset(self, asset: Asset) -> Asset: ...

    def update_asset(self, asset: Asset) -> Asset: ...

    def add_incident(self, incident: Incident) -> Incident: ...

    def get_incident(self, incident_id: str) -> Incident | None: ...


class EngineeringRepository(Protocol):
    def find_tickets(
        self,
        sprint: str | None = None,
        assignee_id: int | None = None,
        status: str | None = None,
    ) -> tuple[JiraTicket, ...]: ...

    def list_blocked_tickets(self) -> tuple[JiraTicket, ...]: ...
