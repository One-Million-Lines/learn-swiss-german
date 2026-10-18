"""FastAPI auth dependencies: current user, CSRF, role enforcement."""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, Request

from app.auth import sessions
from app.common.errors import forbidden, unauthorized
from app.common.security import constant_time_equals, sha256_hex
from app.config import get_settings
from app.db.client import get_db


async def _session_from_request(request: Request) -> Optional[dict]:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        return None
    return await sessions.resolve_access(token)


async def optional_user(request: Request) -> Optional[dict]:
    session = await _session_from_request(request)
    if not session:
        return None
    user = await get_db()["users"].find_one({"_id": session["user_id"]})
    if not user or user.get("status") != "active":
        return None
    request.state.session = session
    return user


async def current_user(request: Request) -> dict:
    user = await optional_user(request)
    if not user:
        raise unauthorized()
    return user


async def require_csrf(request: Request, user: dict = Depends(current_user)) -> dict:
    """Enforce CSRF + Origin for cookie-authenticated, state-changing requests.

    Bearer-token (non-cookie) clients are exempt from the cookie CSRF check.
    """
    settings = get_settings()
    cookie_token = request.cookies.get(settings.session_cookie_name)
    if not cookie_token:
        return user  # Non-cookie client (e.g., native/bearer) — no CSRF cookie flow.

    session = getattr(request.state, "session", None)
    header_csrf = request.headers.get("X-CSRF-Token", "")
    if not session or not header_csrf or not constant_time_equals(
        session.get("csrf_hash", ""), sha256_hex(header_csrf)
    ):
        raise forbidden("CSRF validation failed.", "CSRF_FAILED")

    origin = request.headers.get("Origin") or request.headers.get("Referer") or ""
    if origin and not any(origin.startswith(o) for o in settings.allowed_origins):
        raise forbidden("Origin not allowed.", "ORIGIN_REJECTED")
    return user


def require_roles(*roles: str):
    async def checker(user: dict = Depends(current_user)) -> dict:
        user_roles = set(user.get("roles", []))
        if "administrator" in user_roles:
            return user
        if not user_roles.intersection(roles):
            raise forbidden("You do not have permission for this action.")
        return user

    return checker


async def require_recent_auth(request: Request, user: dict = Depends(current_user)) -> dict:
    session = getattr(request.state, "session", None)
    if not session or not sessions.has_recent_auth(session):
        raise forbidden("This action requires recent authentication.", "RECENT_AUTH_REQUIRED")
    return user
