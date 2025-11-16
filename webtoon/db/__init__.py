"""Database utilities exposed by the webtoon package."""

from __future__ import annotations

from webtoon.db.session import Base, engine, get_session


def init_db() -> None:
    """Create all ORM tables registered on the declarative base."""

    # Import models so they are registered with SQLAlchemy's metadata.
    from webtoon import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


__all__ = ["Base", "engine", "get_session", "init_db"]
