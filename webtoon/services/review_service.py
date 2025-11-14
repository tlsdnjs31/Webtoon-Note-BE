"""TODO: encapsulate review business logic and DB interactions."""

from __future__ import annotations

from typing import Final

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from webtoon.models import Review, WebtoonRatingStats
from webtoon.schemas.review import ReviewCreate


class ReviewService:
    """Coordinates review persistence and rating aggregation."""

    _WEBTOON_EXISTS_QUERY: Final[str] = (
        "SELECT 1 FROM normalized_webtoon WHERE id = :webtoon_id LIMIT 1"
    )

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_review(
        self,
        *,
        webtoon_id: int,
        payload: ReviewCreate,
        anonymous_user_id: str,
    ) -> Review:
        self._ensure_webtoon_exists(webtoon_id)

        review = Review(
            webtoon_id=webtoon_id,
            content=payload.content,
            rating=payload.rating,
            anonymous_user_id=anonymous_user_id,
        )
        self._db.add(review)
        self._db.flush()  # assigns primary key for response serialization

        self._update_rating_stats(webtoon_id, payload.rating)

        try:
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise

        self._db.refresh(review)
        return review

    def _ensure_webtoon_exists(self, webtoon_id: int) -> None:
        exists = self._db.execute(
            text(self._WEBTOON_EXISTS_QUERY), {"webtoon_id": webtoon_id}
        ).scalar()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 웹툰을 찾을 수 없습니다.",
            )

    def _update_rating_stats(self, webtoon_id: int, new_rating: float) -> None:
        stats = self._db.get(WebtoonRatingStats, webtoon_id)

        if stats is None:
            stats = WebtoonRatingStats(
                webtoon_id=webtoon_id,
                average_rating=new_rating,
                review_count=1,
            )
            self._db.add(stats)
            return

        total = stats.average_rating * stats.review_count + new_rating
        stats.review_count += 1
        stats.average_rating = total / stats.review_count
