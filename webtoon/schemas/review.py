"""Request/response schemas for review endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """Payload used when clients submit a new review."""

    content: str = Field(..., min_length=1, max_length=2000)
    rating: float = Field(..., ge=0, le=5)


class ReviewUpdate(BaseModel):
    """Payload used when clients modify an existing review."""

    content: str = Field(..., min_length=1, max_length=2000)
    rating: float = Field(..., ge=0, le=5)


class ReviewResponse(BaseModel):
    """Response schema mirroring the review record returned by the API."""

    id: int
    webtoon_id: str
    content: str
    rating: float
    likes: int
    created_at: datetime
    anonymous_user_id: str
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ReviewListItem(BaseModel):
    """Lightweight representation used when listing reviews."""

    id: int
    content: str
    rating: float
    likes: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ReviewListResponse(BaseModel):
    """Envelope returned by the review list endpoint."""

    webtoon_id: str
    average_rating: float
    review_count: int
    page: int
    limit: int
    reviews: List[ReviewListItem]
