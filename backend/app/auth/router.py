"""Authentication, profile, session and bookmark endpoints (spec 04 §2)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr, Field

from app.auth import service, sessions
from app.auth.deps import current_user, optional_user, require_csrf, require_recent_auth
from app.common.errors import bad_request, not_found
from app.common.ids import new_id
from app.common.security import mask_email
from app.common.serialize import jsonable, public
from app.common.timeutil import utcnow
from app.config import get_settings
from app.db.client import get_db

router = APIRouter(prefix="/api/v1", tags=["auth"])


# --------------------------------------------------------------------------- #
# Cookie helpers                                                               #
# --------------------------------------------------------------------------- #
def _set_auth_cookies(response: Response, creds: dict) -> None:
    settings = get_settings()
    common = {
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": "lax",
        "path": "/",
    }
    if settings.cookie_domain:
        common["domain"] = settings.cookie_domain
    response.set_cookie(settings.session_cookie_name, creds["access_token"],
                        max_age=settings.access_ttl_seconds, **common)
    response.set_cookie(settings.refresh_cookie_name, creds["refresh_token"],
                        max_age=settings.refresh_ttl_seconds, **common)
    # CSRF cookie is readable by JS (double-submit): not HttpOnly.
    csrf_common = {**common, "httponly": False}
    response.set_cookie(settings.csrf_cookie_name, creds["csrf_token"],
                        max_age=settings.refresh_ttl_seconds, **csrf_common)


def _clear_auth_cookies(response: Response) -> None:
    settings = get_settings()
    for name in (settings.session_cookie_name, settings.refresh_cookie_name, settings.csrf_cookie_name):
        response.delete_cookie(name, path="/")


def _public_user(user: dict) -> dict:
    return {
        "id": user["_id"],
        "email": user["email_normalized"],
        "display_name": user.get("display_name"),
        "roles": user.get("roles", []),
        "preferences": user.get("preferences", {}),
        "onboarding": user.get("onboarding", {}),
        "created_at": jsonable(user.get("created_at")),
    }


# --------------------------------------------------------------------------- #
# Magic links                                                                  #
# --------------------------------------------------------------------------- #
class MagicLinkRequest(BaseModel):
    email: EmailStr
    return_path: str = "/auth/callback"
    client_type: str = "web"


@router.post("/auth/magic-links", status_code=202)
async def request_magic_link(payload: MagicLinkRequest, request: Request):
    ip = request.client.host if request.client else "0.0.0.0"
    await service.request_magic_link(
        payload.email, return_path=payload.return_path,
        client_type=payload.client_type, ip=ip,
    )
    # Generic response regardless of account existence.
    return {"data": {"status": "sent", "message": "If the address is valid, a sign-in link is on its way."}}


class ConsumeRequest(BaseModel):
    token: str
    client_type: str = "web"


@router.post("/auth/magic-links/consume")
async def consume_magic_link(payload: ConsumeRequest, response: Response):
    result = await service.consume_magic_link(payload.token, client_type=payload.client_type)
    _set_auth_cookies(response, result["credentials"])
    return {"data": {"user": _public_user(result["user"]),
                     "csrf_token": result["credentials"]["csrf_token"]}}


@router.post("/auth/refresh")
async def refresh(request: Request, response: Response):
    settings = get_settings()
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token:
        raise bad_request("Missing refresh credential.", "NO_REFRESH")
    new_creds = await sessions.rotate_refresh(refresh_token)
    if not new_creds:
        _clear_auth_cookies(response)
        raise bad_request("Refresh failed; please sign in again.", "REFRESH_FAILED")
    _set_auth_cookies(response, new_creds)
    return {"data": {"csrf_token": new_creds["csrf_token"]}}


@router.post("/auth/logout")
async def logout(request: Request, response: Response, user: dict = Depends(optional_user)):
    session = getattr(request.state, "session", None)
    if session:
        await sessions.revoke_family(session["_id"])
    _clear_auth_cookies(response)
    return {"data": {"status": "logged_out"}}


@router.post("/auth/logout-all")
async def logout_all(response: Response, user: dict = Depends(current_user)):
    count = await sessions.revoke_all(user["_id"])
    _clear_auth_cookies(response)
    return {"data": {"status": "logged_out_all", "revoked": count}}


@router.get("/auth/methods")
async def auth_methods():
    # Only enabled methods are advertised; OIDC/native stay hidden until built.
    return {"data": {"methods": ["magic_link"]}}


# --------------------------------------------------------------------------- #
# Profile                                                                      #
# --------------------------------------------------------------------------- #
@router.get("/me")
async def get_me(user: dict = Depends(current_user)):
    return {"data": _public_user(user)}


class PreferencesPatch(BaseModel):
    display_name: Optional[str] = Field(default=None, max_length=80)
    support_language: Optional[str] = None
    ui_language: Optional[str] = None
    active_dialect_id: Optional[str] = None
    timezone: Optional[str] = None
    daily_goal_minutes: Optional[int] = Field(default=None, ge=1, le=600)
    goal: Optional[str] = None
    onboarding_completed: Optional[bool] = None


@router.patch("/me")
async def patch_me(payload: PreferencesPatch, user: dict = Depends(require_csrf)):
    db = get_db()
    updates: dict = {}
    prefs = dict(user.get("preferences", {}))
    for field in ("support_language", "ui_language", "active_dialect_id", "timezone", "daily_goal_minutes", "goal"):
        value = getattr(payload, field)
        if value is not None:
            prefs[field] = value
    updates["preferences"] = prefs
    if payload.display_name is not None:
        updates["display_name"] = payload.display_name
    if payload.onboarding_completed is not None:
        updates["onboarding"] = {**user.get("onboarding", {}), "completed": payload.onboarding_completed}
    updates["updated_at"] = utcnow()
    await db["users"].update_one({"_id": user["_id"]}, {"$set": updates, "$inc": {"version": 1}})
    fresh = await db["users"].find_one({"_id": user["_id"]})
    return {"data": _public_user(fresh)}


@router.get("/me/sessions")
async def my_sessions(request: Request, user: dict = Depends(current_user)):
    db = get_db()
    current_sid = (getattr(request.state, "session", {}) or {}).get("_id")
    cursor = db["sessions"].find({"user_id": user["_id"], "revoked_at": None})
    out = []
    async for s in cursor:
        out.append({
            "id": s["_id"], "client_type": s.get("client_type"),
            "created_at": jsonable(s.get("created_at")),
            "last_seen_at": jsonable(s.get("last_seen_at")),
            "current": s["_id"] == current_sid,
        })
    return {"data": out}


@router.delete("/me/sessions/{session_id}")
async def revoke_session(session_id: str, user: dict = Depends(require_csrf)):
    db = get_db()
    owned = await db["sessions"].find_one({"_id": session_id, "user_id": user["_id"]})
    if not owned:
        raise not_found("Session not found.")
    await sessions.revoke_family(session_id)
    return {"data": {"status": "revoked"}}


# --------------------------------------------------------------------------- #
# Bookmarks                                                                    #
# --------------------------------------------------------------------------- #
class BookmarkIn(BaseModel):
    target_type: str
    target_id: str
    dialect_id: Optional[str] = None


@router.get("/me/bookmarks")
async def list_bookmarks(user: dict = Depends(current_user)):
    db = get_db()
    cursor = db["bookmarks"].find({"user_id": user["_id"]}).sort("created_at", -1)
    return {"data": [public(b) async for b in cursor]}


@router.post("/me/bookmarks")
async def add_bookmark(payload: BookmarkIn, user: dict = Depends(require_csrf)):
    db = get_db()
    doc = {
        "_id": new_id(), "user_id": user["_id"], "target_type": payload.target_type,
        "target_id": payload.target_id, "dialect_id": payload.dialect_id, "created_at": utcnow(),
    }
    await db["bookmarks"].update_one(
        {"user_id": user["_id"], "target_type": payload.target_type,
         "target_id": payload.target_id, "dialect_id": payload.dialect_id},
        {"$setOnInsert": doc}, upsert=True,
    )
    saved = await db["bookmarks"].find_one(
        {"user_id": user["_id"], "target_type": payload.target_type,
         "target_id": payload.target_id, "dialect_id": payload.dialect_id}
    )
    return {"data": public(saved)}


@router.delete("/me/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: str, user: dict = Depends(require_csrf)):
    db = get_db()
    await db["bookmarks"].delete_one({"_id": bookmark_id, "user_id": user["_id"]})
    return {"data": {"status": "deleted"}}


# --------------------------------------------------------------------------- #
# Account export / deletion (job boundaries)                                   #
# --------------------------------------------------------------------------- #
@router.post("/me/exports")
async def request_export(user: dict = Depends(require_recent_auth)):
    """Export the requesting learner's own data (no private grading keys)."""
    db = get_db()
    uid = user["_id"]
    export = {
        "profile": _public_user(user),
        "bookmarks": [public(b) async for b in db["bookmarks"].find({"user_id": uid})],
        "attempts": [
            {k: jsonable(v) for k, v in a.items() if k != "answers"}
            async for a in db["attempts"].find({"user_id": uid})
        ],
        "reward_ledger": [public(r) async for r in db["reward_ledger"].find({"user_id": uid})],
        "enrollments": [public(e) async for e in db["enrollments"].find({"user_id": uid})],
    }
    return {"data": export}


@router.post("/me/deletion")
async def request_deletion(user: dict = Depends(require_recent_auth)):
    """Queue account deletion and revoke sessions immediately."""
    db = get_db()
    await db["users"].update_one({"_id": user["_id"]}, {"$set": {"status": "deleting", "updated_at": utcnow()}})
    await sessions.revoke_all(user["_id"])
    await db["jobs"].update_one(
        {"dedupe_key": f"account_deletion:{user['_id']}"},
        {"$setOnInsert": {
            "_id": new_id(), "dedupe_key": f"account_deletion:{user['_id']}",
            "kind": "account_deletion", "status": "queued",
            "payload": {"user_id": user["_id"]}, "available_at": utcnow(),
            "attempts": 0, "cancel_requested": False, "created_at": utcnow(), "version": 1,
        }}, upsert=True,
    )
    return {"data": {"status": "deletion_queued", "email": mask_email(user["email_normalized"])}}
