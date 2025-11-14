"""Reusable FastAPI dependencies for the webtoon project."""

from webtoon.dependencies.auth import get_anonymous_user_id

__all__ = ["get_anonymous_user_id"]
