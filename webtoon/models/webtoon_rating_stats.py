"""TODO: store aggregate rating stats per webtoon."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, func

from webtoon.db.session import Base


class WebtoonRatingStats(Base):
    """Tracks review counts and average rating per webtoon."""

    __tablename__ = "webtoon_rating_stats"

    webtoon_id = Column(Integer, primary_key=True)
    average_rating = Column(Float, nullable=False, default=0.0, server_default="0")
    review_count = Column(Integer, nullable=False, default=0, server_default="0")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
