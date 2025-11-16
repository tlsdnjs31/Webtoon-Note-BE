"""Endpoints related to anonymous authentication helpers."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from webtoon.dependencies.auth import COOKIE_NAME, get_anonymous_user_id
from webtoon.schemas.auth import AnonymousStatusResponse

router = APIRouter(tags=["auth"])


@router.get(
    "/auth/anonymous",
    response_model=AnonymousStatusResponse,
    status_code=status.HTTP_200_OK,
)
def issue_anonymous_id(request: Request, response: Response) -> AnonymousStatusResponse:
    """Return an existing anon_id cookie or create a new one."""

    anon_id = request.cookies.get(COOKIE_NAME)
    status = "existing"

    if anon_id is None:
        anon_id = get_anonymous_user_id(request, response)
        status = "new"

    return AnonymousStatusResponse(anon_id=anon_id, status=status)
