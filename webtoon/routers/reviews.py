"""Review-related API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from webtoon.db import get_session
from webtoon.dependencies.auth import get_anonymous_user_id
from webtoon.schemas.review import ReviewCreate, ReviewResponse
from webtoon.services.review_service import ReviewService

router = APIRouter(tags=["reviews"])


@router.post("/webtoons/review/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    webtoon_id: int = Query(..., ge=1, description="리뷰를 작성할 웹툰 ID"),
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
