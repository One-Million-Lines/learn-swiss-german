"""Opaque session credentials: access + rotating refresh families with replay
detection and CSRF binding (spec 02 §2)."""
from __future__ import annotations

from datetime import timedelta
from typing import Optional

from app.common.ids import new_id
from app.common.security import random_token, sha256_hex
from app.common.timeutil import utcnow
from app.config import get_settings
from app.db.client import get_db

MAX_USED_REFRESH = 20


async def create_session(user_id: str, client_type: str = "web") -> dict:
    """Create a fresh session family. Returns raw credentials (shown once)."""
    settings = get_settings()
    db = get_db()
    now = utcnow()
    session_id = new_id()
    access_token = random_token(32)
    refresh_token = random_token(32)
    csrf_token = random_token(32)

    doc = {
        "_id": session_id,
        "schema_version": 1,
        "user_id": user_id,
        "access_hash": sha256_hex(access_token),
        "access_expires_at": now + timedelta(seconds=settings.access_ttl_seconds),
        "refresh_hash": sha256_hex(refresh_token),
        "refresh_expires_at": now + timedelta(seconds=settings.refresh_ttl_seconds),
        "used_refresh_hashes": [],
        "family_id": session_id,
        "client_type": client_type,
        "csrf_hash": sha256_hex(csrf_token),
        "created_at": now,
        "last_seen_at": now,
        "recent_auth_at": now,
        "revoked_at": None,
        "expires_at": now + timedelta(seconds=settings.refresh_ttl_seconds),
    }
    await db["sessions"].insert_one(doc)
    return {
        "session_id": session_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "csrf_token": csrf_token,
    }


async def resolve_access(access_token: str) -> Optional[dict]:
    """Return the session doc for a valid, unexpired, unrevoked access token."""
    if not access_token:
        return None
    db = get_db()
    session = await db["sessions"].find_one({"access_hash": sha256_hex(access_token)})
    if not session or session.get("revoked_at"):
        return None
    if session["access_expires_at"] <= utcnow():
        return None
    return session


async def rotate_refresh(refresh_token: str) -> Optional[dict]:
    """Rotate a refresh credential. Detect replay and revoke the family.

    Returns new raw credentials, or None on failure.
    """
    if not refresh_token:
        return None
    db = get_db()
    now = utcnow()
    refresh_hash = sha256_hex(refresh_token)

    # Replay: a previously used refresh value -> revoke the whole family.
    replayed = await db["sessions"].find_one({"used_refresh_hashes": refresh_hash})
    if replayed:
        await db["sessions"].update_one(
            {"_id": replayed["_id"]}, {"$set": {"revoked_at": now}}
        )
        return None

    session = await db["sessions"].find_one({"refresh_hash": refresh_hash})
    if not session or session.get("revoked_at"):
        return None
    if session["refresh_expires_at"] <= now:
        return None

    settings = get_settings()
    new_access = random_token(32)
    new_refresh = random_token(32)
    new_csrf = random_token(32)
    used = (session.get("used_refresh_hashes") or [])[-(MAX_USED_REFRESH - 1):]
    used.append(refresh_hash)

    await db["sessions"].update_one(
        {"_id": session["_id"], "refresh_hash": refresh_hash},
        {
            "$set": {
                "access_hash": sha256_hex(new_access),
                "access_expires_at": now + timedelta(seconds=settings.access_ttl_seconds),
                "refresh_hash": sha256_hex(new_refresh),
                "csrf_hash": sha256_hex(new_csrf),
                "used_refresh_hashes": used,
                "last_seen_at": now,
            }
        },
    )
    return {
        "session_id": session["_id"],
        "user_id": session["user_id"],
        "access_token": new_access,
        "refresh_token": new_refresh,
        "csrf_token": new_csrf,
    }


async def revoke_family(session_id: str) -> None:
    db = get_db()
    await db["sessions"].update_one({"_id": session_id}, {"$set": {"revoked_at": utcnow()}})


async def revoke_all(user_id: str) -> int:
    db = get_db()
    result = await db["sessions"].update_many(
        {"user_id": user_id, "revoked_at": None}, {"$set": {"revoked_at": utcnow()}}
    )
    return result.modified_count


async def mark_recent_auth(session_id: str) -> None:
    db = get_db()
    await db["sessions"].update_one({"_id": session_id}, {"$set": {"recent_auth_at": utcnow()}})


def has_recent_auth(session: dict) -> bool:
    settings = get_settings()
    recent = session.get("recent_auth_at")
    if not recent:
        return False
    return (utcnow() - recent).total_seconds() <= settings.recent_auth_window_seconds
