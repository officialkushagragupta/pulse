"""Domain entities — pure, framework-free representations of the frozen schema.

Immutable (frozen) dataclasses: the domain never mutates an entity in place; adapters
return new instances. These carry NO persistence concerns (no SQLAlchemy) — the ORM
models in infrastructure/ map onto these shapes.

Nullability follows the schema's intent: manager_id, assignee_id, sprint, and the
project/asset dates are optional; everything else is required.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.enums import AssetType, LeaveType, TicketType


@dataclass(frozen=True, slots=True)
class Department:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class Employee:
    id: int
    name: str
    email: str
    dept_id: int
    role: str
    manager_id: int | None
    join_date: date


@dataclass(frozen=True, slots=True)
class Leave:
    id: int
    emp_id: int
    type: LeaveType
    total: int
    used: int
    remaining: int


@dataclass(frozen=True, slots=True)
class Asset:
    id: int
    emp_id: int
    type: AssetType
    status: str
    assigned_date: date | None


@dataclass(frozen=True, slots=True)
class JiraTicket:
    id: int
    key: str
    type: TicketType
    status: str
    priority: str
    assignee_id: int | None
    sprint: str | None
    is_blocked: bool


@dataclass(frozen=True, slots=True)
class Customer:
    id: int
    name: str
    region: str
    segment: str


@dataclass(frozen=True, slots=True)
class Order:
    id: int
    customer_id: int
    amount: Decimal
    order_date: date
    status: str


@dataclass(frozen=True, slots=True)
class Sale:
    id: int
    emp_id: int
    order_id: int
    month: str
    amount: Decimal


@dataclass(frozen=True, slots=True)
class Project:
    id: int
    name: str
    dept_id: int
    status: str
    start_date: date | None
    end_date: date | None


@dataclass(frozen=True, slots=True)
class Incident:
    """An IT incident created by it_create_incident.

    NOTE: the frozen schema has no `incidents` table, so this entity is intentionally
    NOT one of the nine ORM models. Its repository is backed in-memory for Day 1
    (see IncidentRepository); real persistence is a later decision that must NOT alter
    the frozen 9-table contract.
    """

    id: str
    title: str
    description: str
    priority: str
    status: str
