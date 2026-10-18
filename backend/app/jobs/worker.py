"""Job worker: claims leased jobs and runs handlers. Audio synthesis stores
bytes in GridFS and publishes 'ready' metadata only after a successful upload
and a compare-and-set against the active lease (spec 02 §6)."""
from __future__ import annotations

import asyncio
from typing import Optional

from app.ai.gateway import get_speech_provider, validate_audio
from app.common import tracing
from app.common.ids import new_id
from app.common.security import sha256_bytes
from app.common.timeutil import utcnow
from app.content.config_store import get_published_config
from app.db.client import gridfs_bucket, get_db
from app.jobs import queue

AUDIO_KINDS = ["audio_synthesis"]


async def handle_audio_synthesis(job: dict) -> dict:
    db = get_db()
    payload = job["payload"]
    media_id = payload["media_id"]
    text = payload["text"]
    voice_key = payload["voice_key"]

    profiles = (await get_published_config("voice_profiles") or {}).get("profiles", {})
    voice = {"key": voice_key, **profiles.get(voice_key, {})}

    await db["media_assets"].update_one(
        {"_id": media_id, "status": {"$in": ["queued", "failed"]}},
        {"$set": {"status": "generating", "updated_at": utcnow()}},
    )

    provider = get_speech_provider()
    result = provider.synthesize(text=text, voice_profile=voice)
    validate_audio(result)  # reject empty/malformed output before storing

    # Upload bytes to GridFS first; only then publish ready metadata.
    bucket = gridfs_bucket("media")
    checksum = sha256_bytes(result["bytes"])
    file_id = await bucket.upload_from_stream(
        f"audio/{media_id}",
        result["bytes"],
        metadata={"media_id": media_id, "mime": result["mime"], "checksum": checksum},
    )

    # Compare-and-set against the active lease (fencing).
    updated = await db["media_assets"].update_one(
        {"_id": media_id, "status": "generating"},
        {"$set": {
            "status": "ready", "gridfs_file_id": file_id, "content_checksum": checksum,
            "mime": result["mime"], "bytes": len(result["bytes"]),
            "duration_ms": result["duration_ms"],
            "qa": {"validated": True, "provider_request_id": result.get("provider_request_id")},
            "updated_at": utcnow(),
        }},
    )
    if updated.modified_count != 1:
        # A newer lease already finished this asset; discard our orphan upload.
        try:
            await bucket.delete(file_id)
        except Exception:
            pass
        return {"media_id": media_id, "status": "superseded"}

    # Record AI run usage.
    await db["ai_runs"].insert_one({
        "_id": new_id(), "job_id": job["_id"], "purpose": "speech",
        "route_snapshot": {"voice_key": voice_key}, "characters": len(text),
        "actual_cost": result.get("cost_microunits", 0),
        "provider_request_id": result.get("provider_request_id"), "state": "succeeded",
        "created_at": utcnow(),
    })
    return {"media_id": media_id, "status": "ready", "gridfs_file_id": str(file_id)}


async def process_one(worker_id: str) -> bool:
    """Claim and run a single job. Returns True if a job was processed."""
    await queue.reclaim_expired()
    job = await queue.claim_one(worker_id, AUDIO_KINDS)
    if not job:
        return False
    lease_token = job["lease_token"]
    try:
        if job["kind"] == "audio_synthesis":
            result = await handle_audio_synthesis(job)
            await queue.complete(job["_id"], lease_token, result)
        else:
            await queue.fail(job["_id"], lease_token, "unknown job kind", permanent=True)
    except ValueError as exc:
        # Validation failure -> mark media failed, do not retry forever.
        db = get_db()
        await db["media_assets"].update_one(
            {"_id": job["payload"].get("media_id")},
            {"$set": {"status": "failed", "failure_category": "invalid_output", "updated_at": utcnow()}},
        )
        await queue.fail(job["_id"], lease_token, f"validation: {exc}", permanent=True)
        tracing.error("audio_job_invalid", job_id=job["_id"], error=str(exc))
    except Exception as exc:  # transient
        db = get_db()
        await db["media_assets"].update_one(
            {"_id": job["payload"].get("media_id"), "status": "generating"},
            {"$set": {"status": "queued", "failure_category": "transient", "updated_at": utcnow()}},
        )
        await queue.fail(job["_id"], lease_token, f"error: {exc}")
        tracing.error("audio_job_error", job_id=job["_id"], error=str(exc))
    return True


async def run_worker(worker_id: Optional[str] = None, *, poll_interval: float = 1.0) -> None:
    worker_id = worker_id or f"worker-{new_id()[:8]}"
    tracing.info("worker_started", worker_id=worker_id)
    while True:
        processed = await process_one(worker_id)
        if not processed:
            await asyncio.sleep(poll_interval)
