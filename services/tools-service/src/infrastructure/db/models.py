"""SQLAlchemy ORM models — one per frozen-schema table.

These are the persistence shape only; repositories map them to/from the pure domain
entities. Column set matches the frozen contract exactly (no extra columns/tables).
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DepartmentModel(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))


class EmployeeModel(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    dept_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    role: Mapped[str] = mapped_column(String(255))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))
    join_date: Mapped[date]


class LeaveModel(Base):
    __tablename__ = "leaves"

    id: Mapped[int] = mapped_column(primary_key=True)
    emp_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    type: Mapped[str] = mapped_column(String(16))
    total: Mapped[int]
    used: Mapped[int]
    remaining: Mapped[int]


class AssetModel(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    emp_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    type: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(64))
    assigned_date: Mapped[date | None]


class JiraTicketModel(Base):
    __tablename__ = "jira_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(64))
    priority: Mapped[str] = mapped_column(String(64))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))
    sprint: Mapped[str | None] = mapped_column(String(64))
    is_blocked: Mapped[bool] = mapped_column(Boolean)


class CustomerModel(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(64))
    segment: Mapped[str] = mapped_column(String(64))


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    order_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(64))


class SaleModel(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    emp_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    month: Mapped[str] = mapped_column(String(32))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    dept_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    status: Mapped[str] = mapped_column(String(64))
    start_date: Mapped[date | None]
    end_date: Mapped[date | None]
