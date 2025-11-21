"""Helpers for handling anonymous user tracking."""

from __future__ import annotations

import uuid

from fastapi import Request, Response


COOKIE_NAME = "anon_id"


def get_anonymous_user_id(request: Request, response: Response) -> str:
    """Return the anon_id cookie (or issue a new one if missing)."""

    current_id = request.cookies.get(COOKIE_NAME)
    if current_id:
        return current_id

    new_id = str(uuid.uuid4())
    response.set_cookie(
        key=COOKIE_NAME,
        value=new_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 365,  # 1 year
    )
    return new_id
