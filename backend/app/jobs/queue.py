"""Durable MongoDB job queue with atomic claim and fenced leases (spec 02 §6)."""
from __future__ import annotations

from datetime import timedelta
from typing import List, Optional

from pymongo import ReturnDocument

from app.common.ids import new_id
from app.common.security import random_token
from app.common.timeutil import utcnow
from app.db.client import get_db

LEASE_SECONDS = 60
MAX_ATTEMPTS = 4


async def enqueue(kind: str, dedupe_key: str, payload: dict, *, available_at=None, session=None) -> dict:
    """Idempotently enqueue a job by unique dedupe_key."""
    db = get_db()
    now = utcnow()
    await db["jobs"].update_one(
        {"dedupe_key": dedupe_key},
        {"$setOnInsert": {
            "_id": new_id(), "dedupe_key": dedupe_key, "kind": kind, "status": "queued",
            "payload": payload, "available_at": available_at or now, "lease_until": None,
            "lease_token": None, "worker_id": None, "attempts": 0, "cancel_requested": False,
            "result_ref": None, "last_error": None, "next_retry_at": None, "created_at": now,
            "expires_at": None, "version": 1,
        }},
        upsert=True, session=session,
    )
    return await db["jobs"].find_one({"dedupe_key": dedupe_key}, session=session)


async def claim_one(worker_id: str, kinds: List[str]) -> Optional[dict]:
    """Atomically claim the next available job and set a fenced lease."""
    db = get_db()
    now = utcnow()
    token = random_token(16)
    return await db["jobs"].find_one_and_update(
        {"status": "queued", "available_at": {"$lte": now}, "kind": {"$in": kinds}},
        {"$set": {"status": "leased", "lease_token": token, "worker_id": worker_id,
                  "lease_until": now + timedelta(seconds=LEASE_SECONDS)},
         "$inc": {"attempts": 1}},
        sort=[("available_at", 1), ("_id", 1)],
        return_document=ReturnDocument.AFTER,
    )


async def renew_lease(job_id: str, lease_token: str, seconds: int = LEASE_SECONDS) -> bool:
    db = get_db()
    result = await db["jobs"].update_one(
        {"_id": job_id, "lease_token": lease_token},
        {"$set": {"lease_until": utcnow() + timedelta(seconds=seconds)}},
    )
    return result.modified_count == 1


async def complete(job_id: str, lease_token: str, result_ref: dict) -> bool:
    """Finish only if the lease token still matches (fencing)."""
    db = get_db()
    result = await db["jobs"].update_one(
        {"_id": job_id, "lease_token": lease_token, "status": "leased"},
        {"$set": {"status": "succeeded", "result_ref": result_ref, "lease_until": None}},
    )
    return result.modified_count == 1


async def fail(job_id: str, lease_token: str, error: str, *, permanent: bool = False) -> bool:
    db = get_db()
    job = await db["jobs"].find_one({"_id": job_id, "lease_token": lease_token})
    if not job:
        return False
    now = utcnow()
    if permanent or job.get("attempts", 0) >= MAX_ATTEMPTS:
        await db["jobs"].update_one(
            {"_id": job_id, "lease_token": lease_token},
            {"$set": {"status": "failed", "last_error": error, "lease_until": None}},
        )
    else:
        backoff = timedelta(seconds=min(300, 2 ** job.get("attempts", 1)))
        await db["jobs"].update_one(
            {"_id": job_id, "lease_token": lease_token},
            {"$set": {"status": "queued", "last_error": error, "lease_token": None,
                      "worker_id": None, "lease_until": None,
                      "available_at": now + backoff, "next_retry_at": now + backoff}},
        )
    return True


async def reclaim_expired() -> int:
    """Return expired-lease jobs to the queue so another worker can claim them."""
    db = get_db()
    result = await db["jobs"].update_many(
        {"status": "leased", "lease_until": {"$lt": utcnow()}},
        {"$set": {"status": "queued", "lease_token": None, "worker_id": None, "lease_until": None}},
    )
    return result.modified_count
