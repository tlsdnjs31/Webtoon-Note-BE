"""Encapsulates review business logic and DB interactions."""

from __future__ import annotations

from typing import Final, Tuple

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from webtoon.models import Review, ReviewLike, WebtoonRatingStats
from webtoon.schemas.review import ReviewCreate, ReviewUpdate


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
        webtoon_id: str,
        payload: ReviewCreate,
        anonymous_user_id: str,
    ) -> Review:
        self._ensure_webtoon_exists(webtoon_id)

        has_existing = (
            self._db.query(Review.id)
            .filter(
                Review.webtoon_id == webtoon_id,
                Review.anonymous_user_id == anonymous_user_id,
            )
            .first()
        )
        if has_existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 해당 웹툰에 대한 리뷰를 작성했습니다.",
            )

        review = Review(
            webtoon_id=webtoon_id,
            content=payload.content,
            rating=payload.rating,
            anonymous_user_id=anonymous_user_id,
        )
        self._db.add(review)
        self._db.flush()

        self._update_rating_stats(webtoon_id, payload.rating)

        try:
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise

        self._db.refresh(review)
        return review

    def list_reviews(
        self,
        *,
        webtoon_id: str,
        page: int,
        limit: int,
    ) -> Tuple[WebtoonRatingStats, list[Review]]:
        stats = self._db.get(WebtoonRatingStats, webtoon_id)
        if stats is None or stats.review_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 웹툰에 대한 리뷰가 존재하지 않습니다.",
            )

        offset = (page - 1) * limit
        reviews = (
            self._db.query(Review)
            .filter(Review.webtoon_id == webtoon_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return stats, reviews

    def update_review(
        self,
        *,
        webtoon_id: str,
        payload: ReviewUpdate,
        anonymous_user_id: str,
    ) -> Review:
        self._ensure_webtoon_exists(webtoon_id)

        review = (
            self._db.query(Review)
            .filter(
                Review.webtoon_id == webtoon_id,
                Review.anonymous_user_id == anonymous_user_id,
            )
            .order_by(Review.created_at.desc())
            .first()
        )
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own review",
            )

        previous_rating = review.rating
        review.content = payload.content
        review.rating = payload.rating

        self._recalculate_rating_stats(webtoon_id, previous_rating, payload.rating)

        try:
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise

        self._db.refresh(review)
        return review

    def _ensure_webtoon_exists(self, webtoon_id: str) -> None:
        exists = self._db.execute(
            text(self._WEBTOON_EXISTS_QUERY), {"webtoon_id": webtoon_id}
        ).scalar()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 웹툰을 찾을 수 없습니다.",
            )

    def _update_rating_stats(self, webtoon_id: str, new_rating: float) -> None:
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

    def _recalculate_rating_stats(
        self,
        webtoon_id: str,
        previous_rating: float,
        new_rating: float,
    ) -> None:
        stats = self._db.get(WebtoonRatingStats, webtoon_id)
        if stats is None or stats.review_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 웹툰에 대한 리뷰가 존재하지 않습니다.",
            )

        total = stats.average_rating * stats.review_count - previous_rating + new_rating
        stats.average_rating = total / stats.review_count

    def like_review(self, *, review_id: int, anonymous_user_id: str) -> Review:
        review = self._db.get(Review, review_id)
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 리뷰입니다.",
            )

        already_liked = (
            self._db.query(ReviewLike)
            .filter(
                ReviewLike.review_id == review_id,
                ReviewLike.anonymous_user_id == anonymous_user_id,
            )
            .first()
        )
        if already_liked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 좋아요를 누른 사용자입니다.",
            )

        like = ReviewLike(review_id=review_id, anonymous_user_id=anonymous_user_id)
        self._db.add(like)
        review.likes += 1

        try:
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise

        self._db.refresh(review)
        return review
