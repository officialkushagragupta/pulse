"""SQLAlchemy adapter for ItRepository.

Assets are persisted in Postgres. Incidents have no table in the frozen schema, so they
are held in a process-level in-memory store for Day 1 (real persistence is a later
decision that must not alter the frozen 9-table contract).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities import Asset, Incident
from domain.enums import AssetType
from infrastructure.db.models import AssetModel
from shared.errors import EntityNotFound

# Day-1 in-memory incident store (no `incidents` table). Keyed by incident id.
_INCIDENTS: dict[str, Incident] = {}


def _to_asset(m: AssetModel) -> Asset:
    return Asset(
        id=m.id,
        emp_id=m.emp_id,
        type=AssetType(m.type),
        status=m.status,
        assigned_date=m.assigned_date,
    )


class SqlAlchemyItRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_asset(self, employee_id: int, asset_type: AssetType) -> Asset | None:
        stmt = (
            select(AssetModel)
            .where(AssetModel.emp_id == employee_id, AssetModel.type == asset_type.value)
            .limit(1)
        )
        model = self._session.scalars(stmt).first()
        return _to_asset(model) if model else None

    def add_asset(self, asset: Asset) -> Asset:
        model = AssetModel(
            emp_id=asset.emp_id,
            type=asset.type.value,
            status=asset.status,
            assigned_date=asset.assigned_date,
        )
        self._session.add(model)
        self._session.flush()  # assign the DB id; the api boundary commits
        return _to_asset(model)

    def update_asset(self, asset: Asset) -> Asset:
        model = self._session.get(AssetModel, asset.id)
        if model is None:
            raise EntityNotFound(f"asset {asset.id}")
        model.status = asset.status
        model.assigned_date = asset.assigned_date
        self._session.flush()
        return _to_asset(model)

    def add_incident(self, incident: Incident) -> Incident:
        _INCIDENTS[incident.id] = incident
        return incident

    def get_incident(self, incident_id: str) -> Incident | None:
        return _INCIDENTS.get(incident_id)
