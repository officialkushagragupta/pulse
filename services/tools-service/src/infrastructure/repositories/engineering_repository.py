"""SQLAlchemy adapter for EngineeringRepository."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities import JiraTicket
from domain.enums import TicketType
from infrastructure.db.models import JiraTicketModel


def _to_ticket(m: JiraTicketModel) -> JiraTicket:
    return JiraTicket(
        id=m.id,
        key=m.key,
        type=TicketType(m.type),
        status=m.status,
        priority=m.priority,
        assignee_id=m.assignee_id,
        sprint=m.sprint,
        is_blocked=m.is_blocked,
    )


class SqlAlchemyEngineeringRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_tickets(
        self,
        sprint: str | None = None,
        assignee_id: int | None = None,
        status: str | None = None,
    ) -> tuple[JiraTicket, ...]:
        stmt = select(JiraTicketModel)
        if sprint is not None:
            stmt = stmt.where(JiraTicketModel.sprint == sprint)
        if assignee_id is not None:
            stmt = stmt.where(JiraTicketModel.assignee_id == assignee_id)
        if status is not None:
            stmt = stmt.where(JiraTicketModel.status == status)
        return tuple(_to_ticket(m) for m in self._session.scalars(stmt))

    def list_blocked_tickets(self) -> tuple[JiraTicket, ...]:
        stmt = select(JiraTicketModel).where(JiraTicketModel.is_blocked.is_(True))
        return tuple(_to_ticket(m) for m in self._session.scalars(stmt))
