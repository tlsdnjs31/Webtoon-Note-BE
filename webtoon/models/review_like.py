"""Tracks which anonymous users liked which reviews."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from webtoon.db.session import Base


class ReviewLike(Base):
    """Association table storing unique (review_id, anonymous_user_id) pairs."""

    __tablename__ = "review_likes"

    review_id = Column(
        Integer,
        ForeignKey("reviews.id", ondelete="CASCADE"),
        primary_key=True,
    )
    anonymous_user_id = Column(String(36), primary_key=True)
    liked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
