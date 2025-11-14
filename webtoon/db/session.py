"""SQLAlchemy session helpers for the webtoon backend."""

from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from webtoon.database import DB_PATH


class Base(DeclarativeBase):
    """Base class for all ORM models."""


DATABASE_URL = f"sqlite:///{DB_PATH}"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session that is cleaned up after the request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
