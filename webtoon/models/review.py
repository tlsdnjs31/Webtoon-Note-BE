"""SQLAlchemy model describing individual webtoon reviews."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from webtoon.db.session import Base


class Review(Base):
    """Represents a user-submitted review for a specific webtoon."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    webtoon_id = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    likes = Column(Integer, nullable=False, default=0, server_default="0")
    anonymous_user_id = Column(String(36), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
