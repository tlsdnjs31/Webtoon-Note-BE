"""Schemas for authentication-related endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class AnonymousStatusResponse(BaseModel):
    """Represents the anon_id status returned by /auth/anonymous."""

    anon_id: str
    status: Literal["new", "existing"]
