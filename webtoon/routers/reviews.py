"""Review-related API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from webtoon.db import get_session
from webtoon.dependencies.auth import get_anonymous_user_id
from webtoon.schemas.review import (
    ReviewCreate,
    ReviewLikeResponse,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)
from webtoon.services.review_service import ReviewService

router = APIRouter(tags=["reviews"])


@router.post("/webtoons/review/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    webtoon_id: str = Query(..., min_length=1, description="리뷰를 작성할 웹툰 ID"),
    db: Session = Depends(get_session),
    anonymous_user_id: str = Depends(get_anonymous_user_id),
) -> ReviewResponse:
    """Create a new review and update the corresponding rating stats."""

    service = ReviewService(db)
    review = service.create_review(
        webtoon_id=webtoon_id,
        payload=payload,
        anonymous_user_id=anonymous_user_id,
    )
    return ReviewResponse.model_validate(review)


@router.get(
    "/webtoons/{webtoon_id}/reviews",
    response_model=ReviewListResponse,
    status_code=status.HTTP_200_OK,
)
def list_reviews(
    webtoon_id: str = Path(..., min_length=1, description="리뷰를 조회할 웹툰 ID"),
    page: int = Query(1, ge=1, description="조회할 페이지 번호"),
    limit: int = Query(10, ge=1, description="한 페이지당 가져올 리뷰 개수"),
    db: Session = Depends(get_session),
) -> ReviewListResponse:
    """Return paginated reviews for a specific webtoon."""

    service = ReviewService(db)
    stats, reviews = service.list_reviews(webtoon_id=webtoon_id, page=page, limit=limit)
    return ReviewListResponse(
        webtoon_id=stats.webtoon_id,
        average_rating=stats.average_rating,
        review_count=stats.review_count,
        page=page,
        limit=limit,
        reviews=reviews,
    )


@router.put(
    "/webtoons/{webtoon_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
)
def update_review(
    payload: ReviewUpdate,
    webtoon_id: str = Path(..., min_length=1, description="수정할 리뷰의 웹툰 ID"),
    db: Session = Depends(get_session),
    anonymous_user_id: str = Depends(get_anonymous_user_id),
) -> ReviewResponse:
    """Update the review authored by the anon user for the given webtoon."""

    service = ReviewService(db)
    review = service.update_review(
        webtoon_id=webtoon_id,
        payload=payload,
        anonymous_user_id=anonymous_user_id,
    )
    return ReviewResponse.model_validate(review)


@router.post(
    "/reviews/{review_id}/like",
    response_model=ReviewLikeResponse,
    status_code=status.HTTP_200_OK,
)
def like_review(
    review_id: int = Path(..., ge=1, description="좋아요를 누를 리뷰 ID"),
    db: Session = Depends(get_session),
    anonymous_user_id: str = Depends(get_anonymous_user_id),
) -> ReviewLikeResponse:
    """Register a like for the given review on behalf of the anon user."""

    service = ReviewService(db)
    review = service.like_review(review_id=review_id, anonymous_user_id=anonymous_user_id)
    return ReviewLikeResponse(review_id=review.id, likes=review.likes)
