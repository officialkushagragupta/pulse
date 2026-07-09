"""Database plumbing: engine, session factory, schema creation.

This module ONLY builds resources — it does not open, commit, or close sessions. The
per-request session lifecycle is owned by the api layer (see api/dependencies.get_session):
a session is created when a request arrives and committed/rolled-back/closed when it leaves.
Repositories receive an already-open Session and never manage its lifecycle.
"""
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from infrastructure.config import get_settings
from infrastructure.db.models import Base


def build_engine() -> Engine:
    return create_engine(get_settings().postgres_dsn, pool_pre_ping=True, future=True)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def create_all(engine: Engine) -> None:
    Base.metadata.create_all(engine)
