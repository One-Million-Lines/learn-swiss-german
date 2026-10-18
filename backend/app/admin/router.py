"""Admin API (spec 01 §8, 04 §2). Capabilities enforced server-side via RBAC."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.admin import audit
from app.auth.deps import current_user, require_csrf, require_recent_auth, require_roles
from app.common.errors import bad_request, conflict, not_found
from app.common.ids import new_id
from app.common.serialize import jsonable, public
from app.common.timeutil import utcnow
from app.db.client import get_db
from app.db.schema import ALL_COLLECTIONS, INDEXES

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

editor = require_roles("editor", "publisher")
publisher = require_roles("publisher")
administrator = require_roles("administrator")


# --------------------------------------------------------------------------- #
# Content lifecycle                                                            #
# --------------------------------------------------------------------------- #
@router.get("/content")
async def list_content(kind: Optional[str] = None, status: Optional[str] = None,
                       dialect_id: Optional[str] = None, limit: int = Query(20, le=100),
                       user: dict = Depends(editor)):
    db = get_db()
    query: Dict[str, Any] = {}
    if kind:
        query["kind"] = kind
    if status:
        query["status"] = status
    if dialect_id:
        query["dialect_id"] = dialect_id
    cursor = db["content_items"].find(query).sort("updated_at", -1).limit(limit)
    return {"data": [public(c) async for c in cursor]}


class ContentCreate(BaseModel):
    kind: str
    slug: str
    dialect_id: Optional[str] = None
    title: Optional[str] = None
    payload: Dict[str, Any] = {}
    private_grading: Optional[Dict[str, Any]] = None


@router.post("/content")
async def create_content(payload: ContentCreate, user: dict = Depends(editor)):
    db = get_db()
    existing = await db["content_items"].find_one({"kind": payload.kind, "slug": payload.slug})
    if existing:
        raise conflict("An item with this kind/slug already exists.", "SLUG_EXISTS")
    now = utcnow()
    item_id = new_id()
    item = {
        "_id": item_id, "schema_version": 1, "kind": payload.kind, "slug": payload.slug,
        "dialect_id": payload.dialect_id, "scenario_id": None, "legacy_id": None,
        "status": "draft", "published_revision": None, "draft_revision": 1,
        "discovery": {}, "title": payload.title, "summary": None, "tags": [],
        "topic_id": None, "subtopic_id": None, "search_text": (payload.title or "").lower(),
        "sort_order": 0, "created_at": now, "updated_at": now, "version": 1,
    }
    revision = {
        "_id": new_id(), "schema_version": 1, "item_id": item_id, "revision": 1,
        "kind": payload.kind, "dialect_id": payload.dialect_id, "status": "draft",
        "payload": payload.payload, "private_grading": payload.private_grading,
        "references": [], "provenance": {"source": "admin", "actor": user["_id"]},
        "qa": None, "created_by": user["_id"], "created_at": now, "updated_at": now, "version": 1,
    }
    await db["content_items"].insert_one(item)
    await db["content_revisions"].insert_one(revision)
    await audit.record(actor_user_id=user["_id"], action="content.create",
                       target_type="content_item", target_id=item_id)
    return {"data": public(item)}


@router.get("/content/{item_id}/revisions")
async def list_revisions(item_id: str, user: dict = Depends(editor)):
    db = get_db()
    cursor = db["content_revisions"].find({"item_id": item_id}).sort("revision", 1)
    return {"data": [public(r) async for r in cursor]}


async def _transition(item_id: str, from_status: List[str], to_status: str, actor: str, action: str):
    db = get_db()
    item = await db["content_items"].find_one({"_id": item_id})
    if not item:
        raise not_found("Content item not found.")
    draft_rev = item.get("draft_revision") or item.get("published_revision")
    rev = await db["content_revisions"].find_one({"item_id": item_id, "revision": draft_rev})
    if not rev or rev.get("status") not in from_status:
        raise conflict(f"Cannot transition from current state ({rev.get('status') if rev else 'none'}).", "INVALID_TRANSITION")
    await db["content_revisions"].update_one(
        {"_id": rev["_id"]}, {"$set": {"status": to_status, "updated_at": utcnow()}})
    await db["content_items"].update_one(
        {"_id": item_id}, {"$set": {"status": to_status, "updated_at": utcnow()}})
    await audit.record(actor_user_id=actor, action=action, target_type="content_item",
                       target_id=item_id, before_ref={"status": rev.get("status")},
                       after_ref={"status": to_status})
    return rev


@router.post("/content/{item_id}/submit-review")
async def submit_review(item_id: str, user: dict = Depends(editor)):
    await _transition(item_id, ["draft", "generated"], "in_review", user["_id"], "content.submit_review")
    return {"data": {"status": "in_review"}}


@router.post("/content/{item_id}/approve")
async def approve(item_id: str, user: dict = Depends(publisher)):
    await _transition(item_id, ["in_review"], "approved", user["_id"], "content.approve")
    return {"data": {"status": "approved"}}


@router.post("/content/{item_id}/publish")
async def publish(item_id: str, user: dict = Depends(publisher)):
    db = get_db()
    item = await db["content_items"].find_one({"_id": item_id})
    if not item:
        raise not_found("Content item not found.")
    rev_num = item.get("draft_revision") or item.get("published_revision")
    rev = await db["content_revisions"].find_one({"item_id": item_id, "revision": rev_num})
    if not rev or rev.get("status") != "approved":
        raise conflict("Only approved revisions can be published.", "NOT_APPROVED")

    # Publication gate: no answer leakage into public payload.
    if (rev.get("payload") or {}).get("correct_choice_id") or (rev.get("payload") or {}).get("answer"):
        raise bad_request("Answer keys must live in private_grading, not the public payload.", "ANSWER_LEAK")

    now = utcnow()
    await db["content_revisions"].update_one({"_id": rev["_id"]}, {"$set": {"status": "published", "updated_at": now}})
    await db["content_items"].update_one(
        {"_id": item_id},
        {"$set": {"status": "published", "published_revision": rev_num, "updated_at": now}})
    await audit.record(actor_user_id=user["_id"], action="content.publish",
                       target_type="content_item", target_id=item_id,
                       after_ref={"revision": rev_num})
    return {"data": {"status": "published", "revision": rev_num}}


@router.post("/content/{item_id}/withdraw")
async def withdraw(item_id: str, user: dict = Depends(publisher)):
    db = get_db()
    item = await db["content_items"].find_one({"_id": item_id})
    if not item:
        raise not_found("Content item not found.")
    await db["content_items"].update_one(
        {"_id": item_id}, {"$set": {"status": "archived", "updated_at": utcnow()}})
    await audit.record(actor_user_id=user["_id"], action="content.withdraw",
                       target_type="content_item", target_id=item_id)
    return {"data": {"status": "archived"}}


# --------------------------------------------------------------------------- #
# AI generation jobs                                                           #
# --------------------------------------------------------------------------- #
class GenerationBrief(BaseModel):
    route_alias: str = "lesson.author"
    situation: str
    learner_outcome: str
    dialect_id: str
    number_of_turns: int = 8
    register_style: str = "neutral"
    support_languages: List[str] = ["en", "es"]
    batch_size: int = 1


@router.post("/generations")
async def create_generation(brief: GenerationBrief, user: dict = Depends(editor)):
    if brief.batch_size > 20:
        raise bad_request("Batch size is capped at 20.", "BATCH_TOO_LARGE")
    from app.jobs import queue

    job = await queue.enqueue(
        "ai_generation", f"generation:{new_id()}",
        {"brief": brief.model_dump(), "actor": user["_id"]},
    )
    await audit.record(actor_user_id=user["_id"], action="generation.create",
                       target_type="job", target_id=job["_id"])
    return {"data": {"job_id": job["_id"], "status": job["status"],
                     "note": "Generation is asynchronous and never auto-publishes."}}


# --------------------------------------------------------------------------- #
# Users & roles                                                                #
# --------------------------------------------------------------------------- #
@router.get("/users")
async def list_users(q: Optional[str] = None, limit: int = Query(20, le=100),
                     user: dict = Depends(administrator)):
    db = get_db()
    query = {}
    if q:
        query["email_normalized"] = {"$regex": q.lower()}
    cursor = db["users"].find(query, {"preferences": 0}).limit(limit)
    return {"data": [{"id": u["_id"], "email": u["email_normalized"], "roles": u.get("roles", []),
                      "status": u.get("status"), "created_at": jsonable(u.get("created_at"))}
                     async for u in cursor]}


class RolesIn(BaseModel):
    roles: List[str]


@router.post("/users/{user_id}/roles")
async def set_roles(user_id: str, payload: RolesIn, admin: dict = Depends(require_recent_auth)):
    if "administrator" not in admin.get("roles", []):
        raise bad_request("Only administrators can change roles.", "FORBIDDEN")
    allowed = {"editor", "publisher", "administrator"}
    if not set(payload.roles).issubset(allowed):
        raise bad_request("Unknown role.", "INVALID_ROLE")
    db = get_db()
    target = await db["users"].find_one({"_id": user_id})
    if not target:
        raise not_found("User not found.")
    await db["users"].update_one({"_id": user_id},
                                 {"$set": {"roles": payload.roles, "updated_at": utcnow()},
                                  "$inc": {"version": 1}})
    await audit.record(actor_user_id=admin["_id"], action="user.set_roles",
                       target_type="user", target_id=user_id,
                       before_ref={"roles": target.get("roles", [])}, after_ref={"roles": payload.roles})
    return {"data": {"id": user_id, "roles": payload.roles}}


@router.post("/users/{user_id}/suspend")
async def suspend_user(user_id: str, admin: dict = Depends(require_recent_auth)):
    if "administrator" not in admin.get("roles", []):
        raise bad_request("Only administrators can suspend users.", "FORBIDDEN")
    db = get_db()
    from app.auth import sessions

    await db["users"].update_one({"_id": user_id}, {"$set": {"status": "suspended", "updated_at": utcnow()}})
    await sessions.revoke_all(user_id)
    await audit.record(actor_user_id=admin["_id"], action="user.suspend",
                       target_type="user", target_id=user_id)
    return {"data": {"id": user_id, "status": "suspended"}}


# --------------------------------------------------------------------------- #
# Creators & reports (moderation)                                              #
# --------------------------------------------------------------------------- #
class CreatorIn(BaseModel):
    slug: str
    name: str
    bio: Optional[str] = None
    profile_links: List[dict] = []
    dialect_ids: List[str] = []
    topic_ids: List[str] = []
    attribution: Optional[dict] = None
    featured_order: Optional[int] = None


@router.post("/creators")
async def create_creator(payload: CreatorIn, user: dict = Depends(editor)):
    db = get_db()
    if not payload.profile_links:
        raise bad_request("A real, verified profile/source link is required.", "SOURCE_REQUIRED")
    now = utcnow()
    doc = {
        "_id": new_id(), "slug": payload.slug, "name": payload.name, "bio": payload.bio,
        "profile_links": payload.profile_links, "dialect_ids": payload.dialect_ids,
        "topic_ids": payload.topic_ids, "attribution": payload.attribution,
        "verification": {"verified_at": None}, "image_media_id": None, "status": "draft",
        "featured_order": payload.featured_order, "feature_window": None,
        "created_at": now, "updated_at": now, "version": 1,
    }
    await db["creators"].update_one({"slug": payload.slug}, {"$setOnInsert": doc}, upsert=True)
    saved = await db["creators"].find_one({"slug": payload.slug})
    await audit.record(actor_user_id=user["_id"], action="creator.create",
                       target_type="creator", target_id=saved["_id"])
    return {"data": public(saved)}


@router.post("/creators/{creator_id}/publish")
async def publish_creator(creator_id: str, user: dict = Depends(publisher)):
    db = get_db()
    await db["creators"].update_one(
        {"_id": creator_id},
        {"$set": {"status": "published", "verification.verified_at": utcnow(), "updated_at": utcnow()}})
    await audit.record(actor_user_id=user["_id"], action="creator.publish",
                       target_type="creator", target_id=creator_id)
    return {"data": {"status": "published"}}


@router.post("/creators/{creator_id}/hide")
async def hide_creator(creator_id: str, user: dict = Depends(publisher)):
    db = get_db()
    await db["creators"].update_one({"_id": creator_id},
                                    {"$set": {"status": "hidden", "featured_order": None, "updated_at": utcnow()}})
    await audit.record(actor_user_id=user["_id"], action="creator.hide",
                       target_type="creator", target_id=creator_id)
    return {"data": {"status": "hidden"}}


@router.get("/reports")
async def list_reports(status: str = "open", user: dict = Depends(editor)):
    db = get_db()
    cursor = db["reports"].find({"status": status}).sort("created_at", 1).limit(100)
    return {"data": [public(r) async for r in cursor]}


# --------------------------------------------------------------------------- #
# Operations: jobs, usage, audit, database health                             #
# --------------------------------------------------------------------------- #
@router.get("/jobs")
async def list_jobs(status: Optional[str] = None, user: dict = Depends(editor)):
    db = get_db()
    query = {"status": status} if status else {}
    cursor = db["jobs"].find(query).sort("created_at", -1).limit(50)
    return {"data": [{"id": j["_id"], "kind": j["kind"], "status": j["status"],
                      "attempts": j.get("attempts"), "last_error": j.get("last_error"),
                      "created_at": jsonable(j.get("created_at"))} async for j in cursor]}


@router.get("/usage")
async def usage(user: dict = Depends(editor)):
    db = get_db()
    total_runs = await db["ai_runs"].count_documents({})
    ready_audio = await db["media_assets"].count_documents({"status": "ready"})
    failed_audio = await db["media_assets"].count_documents({"status": "failed"})
    total_audio = await db["media_assets"].count_documents({})
    hit_ratio = (ready_audio / total_audio) if total_audio else 0.0
    return {"data": {"ai_runs": total_runs, "audio_ready": ready_audio, "audio_failed": failed_audio,
                     "audio_cache_hit_ratio": round(hit_ratio, 3)}}


@router.get("/audit")
async def list_audit(limit: int = Query(50, le=200), user: dict = Depends(administrator)):
    db = get_db()
    cursor = db["audit_log"].find({}).sort("created_at", -1).limit(limit)
    return {"data": [public(a) async for a in cursor]}


@router.get("/database-health")
async def database_health(user: dict = Depends(administrator)):
    """Index/collection manifest health. No raw query console (spec 01 §8)."""
    db = get_db()
    collections = await db.list_collection_names()
    missing_collections = [c for c in ALL_COLLECTIONS if c not in collections]
    index_report = []
    for collection, keys, name, options in INDEXES:
        try:
            existing = {ix["name"] async for ix in db[collection].list_indexes()}
            index_report.append({"collection": collection, "index": name,
                                 "present": name in existing})
        except Exception:
            index_report.append({"collection": collection, "index": name, "present": False})
    missing_indexes = [r for r in index_report if not r["present"]]
    return {"data": {
        "collections_total": len(ALL_COLLECTIONS),
        "missing_collections": missing_collections,
        "indexes_total": len(INDEXES),
        "missing_indexes": missing_indexes,
        "healthy": not missing_collections and not missing_indexes,
    }}
