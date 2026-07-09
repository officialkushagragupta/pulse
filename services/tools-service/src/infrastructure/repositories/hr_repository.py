"""SQLAlchemy adapter for HrRepository."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities import Employee, Leave
from domain.enums import LeaveType
from infrastructure.db.models import EmployeeModel, LeaveModel


def _to_employee(m: EmployeeModel) -> Employee:
    return Employee(
        id=m.id,
        name=m.name,
        email=m.email,
        dept_id=m.dept_id,
        role=m.role,
        manager_id=m.manager_id,
        join_date=m.join_date,
    )


def _to_leave(m: LeaveModel) -> Leave:
    return Leave(
        id=m.id,
        emp_id=m.emp_id,
        type=LeaveType(m.type),
        total=m.total,
        used=m.used,
        remaining=m.remaining,
    )


class SqlAlchemyHrRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_employee(self, employee_id: int) -> Employee | None:
        model = self._session.get(EmployeeModel, employee_id)
        return _to_employee(model) if model else None

    def find_employee(self, name_or_id: str) -> Employee | None:
        if name_or_id.isdigit():
            return self.get_employee(int(name_or_id))
        stmt = (
            select(EmployeeModel)
            .where((EmployeeModel.name == name_or_id) | (EmployeeModel.email == name_or_id))
            .limit(1)
        )
        model = self._session.scalars(stmt).first()
        return _to_employee(model) if model else None

    def list_leaves(self, employee_id: int) -> tuple[Leave, ...]:
        stmt = select(LeaveModel).where(LeaveModel.emp_id == employee_id)
        return tuple(_to_leave(m) for m in self._session.scalars(stmt))
