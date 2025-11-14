"""SQLAlchemy engine and session helpers for the webtoon service."""

from __future__ import annotations

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "webtoon_database.sqlite"
DATABASE_URL = f"sqlite:///{DB_FILE}"


class Base(DeclarativeBase):
    """Declarative base class shared by all ORM models."""


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    """Provide a scoped SQLAlchemy session for request handlers."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
