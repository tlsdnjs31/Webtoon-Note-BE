"""ORM mapping for storing user reviews on webtoons."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from webtoon.db.session import Base


class Review(Base):
    """Represents a single user review for a specific webtoon."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    likes = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    anonymous_user_id = Column(String(length=64), nullable=False, index=True)
