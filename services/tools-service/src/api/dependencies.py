"""Composition root (grows through T10).

Sessions are created and maintained HERE, at the api boundary: `get_session` is a
request-scoped FastAPI dependency that opens one Session per request and
commits / rolls-back / closes it at the request edge. Repositories and use cases
receive that open Session; they never open or close it themselves.
"""
from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from infrastructure.db.session import build_engine, build_session_factory, create_all


@lru_cache
def _engine() -> Engine:
    engine = build_engine()
    create_all(engine)  # T3: create tables on first use (T10 may move to a lifespan hook)
    return engine


@lru_cache
def _session_factory() -> sessionmaker[Session]:
    return build_session_factory(_engine())


def get_session() -> Iterator[Session]:
    session = _session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
