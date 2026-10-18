"""Lazy audio: resolve request -> fingerprint -> cache hit or durable job."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.auth import rate_limit
from app.common.errors import bad_request, forbidden, not_found, unavailable
from app.common.ids import new_id
from app.common.timeutil import utcnow
from app.content.canonical import audio_fingerprint, audio_key
from app.content.config_store import get_published_config
from app.db.client import get_db
from app.db.tx import in_transaction
from app.jobs import queue

DEV_VOICE_KEY = "voice.dev_fake"


async def _resolve_voice_profile(dialect_id: Optional[str]) -> Dict[str, Any]:
    profiles = (await get_published_config("voice_profiles") or {}).get("profiles", {})
    # Prefer a dialect-matched enabled profile; fall back to the dev profile.
    for key, prof in profiles.items():
        if prof.get("dialect_id") == dialect_id and prof.get("status") in ("enabled", "enabled_dev"):
            return {"key": key, **prof}
    if DEV_VOICE_KEY in profiles:
        return {"key": DEV_VOICE_KEY, **profiles[DEV_VOICE_KEY]}
    raise unavailable("No approved voice profile is available for this dialect.", "NO_VOICE_PROFILE")


async def _resolve_utterance(content_ref: dict, turn_id: str) -> dict:
    db = get_db()
    item_id = content_ref.get("item_id")
    revision_num = content_ref.get("revision")
    item = await db["content_items"].find_one({"_id": item_id})
    if not item or item.get("status") not in ("published",):
        raise not_found("Content is not available.")
    revision = await db["content_revisions"].find_one({"item_id": item_id, "revision": revision_num})
    if not revision:
        raise not_found("Content revision not found.")
    turn = next((t for t in revision["payload"].get("turns", []) if t.get("id") == turn_id), None)
    if not turn or not turn.get("utterance_id"):
        raise not_found("Turn not found.")
    utterance = await db["utterances"].find_one({"_id": turn["utterance_id"]})
    if not utterance:
        raise not_found("Utterance not found.")
    return {"utterance": utterance, "item": item}


def _fingerprint_for(utterance: dict, voice: Dict[str, Any]) -> Dict[str, Any]:
    return audio_fingerprint(
        text_sha256_value=utterance["text_sha256"],
        language_tag=utterance["language_tag"],
        dialect_id=utterance.get("dialect_id"),
        pronunciation_context_id=utterance.get("pronunciation_context_id", "default"),
        spoken_text_sha256=utterance["text_sha256"],
        provider=voice["provider"],
        model=voice["model"],
        model_revision=voice.get("model_revision", "v1"),
        voice_id=voice["voice_id"],
        voice_profile_version=voice.get("voice_profile_version", 1),
        synthesis_version=voice.get("synthesis_version", 1),
        pronunciation_lexicon_version=voice.get("pronunciation_lexicon_version", 1),
        fmt=voice.get("format", "wav"),
        sample_rate_hz=voice.get("sample_rate_hz", 24000),
    )


def _asset_ready_response(asset: dict) -> dict:
    return {
        "status": "ready",
        "media_id": asset["_id"],
        "audio_key": asset.get("audio_key"),
        "utterance_id": asset.get("utterance_id"),
        "stream_url": f"/api/v1/media/{asset['_id']}/stream",
        "duration_ms": asset.get("duration_ms"),
        "ai_generated": True,
        "human_reviewed": asset.get("human_reviewed", False),
    }


async def request_audio(*, content_ref: dict, turn_id: str, user: Optional[dict]) -> Dict[str, Any]:
    db = get_db()
    resolved = await _resolve_utterance(content_ref, turn_id)
    utterance = resolved["utterance"]
    voice = await _resolve_voice_profile(utterance.get("dialect_id"))
    fp = _fingerprint_for(utterance, voice)
    key = audio_key(fp)

    existing = await db["media_assets"].find_one({"audio_key": key})
    if existing and existing.get("status") == "ready":
        return _asset_ready_response(existing)

    # Cache miss -> generation requires an authenticated learner (cost control).
    if user is None:
        raise forbidden("Sign in to generate new audio.", "LOGIN_REQUIRED_FOR_GENERATION")

    # Budget cap (global).
    if not await _budget_available():
        raise unavailable("New audio is temporarily unavailable.", "AUDIO_BUDGET_EXHAUSTED", retry_after=3600)

    # Per-user generation limits (only on genuine misses).
    budgets = await get_published_config("budgets") or {}
    ok = (
        await rate_limit.check_and_increment(
            f"audio:day:{user['_id']}", limit=budgets.get("audio_uncached_per_user_per_day", 30),
            window_seconds=86400)
        and await rate_limit.check_and_increment(
            f"audio:min:{user['_id']}", limit=budgets.get("audio_new_requests_per_user_per_minute", 5),
            window_seconds=60)
    )
    if not ok:
        raise unavailable("You have reached today's audio generation limit.", "AUDIO_LIMIT_REACHED", retry_after=60)

    now = utcnow()

    async def _txn(session):
        # One media_asset per unique audio_key.
        await db["media_assets"].update_one(
            {"audio_key": key},
            {"$setOnInsert": {
                "_id": new_id(), "type": "audio", "status": "queued", "audio_key": key,
                "utterance_id": utterance["_id"], "fingerprint": fp, "gridfs_file_id": None,
                "content_checksum": None, "mime": None, "bytes": None, "duration_ms": None,
                "route_ref": {"voice_key": voice["key"]},
                "voice_profile_ref": {"key": voice["key"], "version": voice.get("voice_profile_version", 1)},
                "visibility": "public", "human_reviewed": bool(voice.get("human_reviewed", False)),
                "ai_generated": True, "qa": None, "failure_category": None,
                "created_at": now, "version": 1,
            }},
            upsert=True, session=session,
        )
        asset_doc = await db["media_assets"].find_one({"audio_key": key}, session=session)
        await queue.enqueue(
            "audio_synthesis", f"audio:{key}",
            {"audio_key": key, "media_id": asset_doc["_id"], "utterance_id": utterance["_id"],
             "voice_key": voice["key"], "text": utterance["text"]},
            session=session,
        )
        return asset_doc

    await in_transaction(_txn)

    asset = await db["media_assets"].find_one({"audio_key": key})
    if asset.get("status") == "ready":
        return _asset_ready_response(asset)
    return {
        "status": "queued" if asset.get("status") == "queued" else asset.get("status"),
        "request_id": asset["_id"],
        "status_url": f"/api/v1/audio/requests/{asset['_id']}",
        "poll_after_seconds": 2,
    }


async def audio_request_status(request_id: str) -> dict:
    db = get_db()
    asset = await db["media_assets"].find_one({"_id": request_id})
    if not asset:
        raise not_found("Audio request not found.")
    if asset.get("status") == "ready":
        return _asset_ready_response(asset)
    if asset.get("status") == "failed":
        return {"status": "failed", "request_id": request_id,
                "failure_category": asset.get("failure_category"),
                "message": "Audio could not be generated. Text learning is unaffected."}
    return {"status": asset.get("status"), "request_id": request_id,
            "status_url": f"/api/v1/media/{request_id}/stream", "poll_after_seconds": 2}


async def _budget_available() -> bool:
    """Global daily provider spend cap check (simplified reservation model)."""
    from app.config import get_settings
    from app.common.timeutil import editorial_date

    db = get_db()
    settings = get_settings()
    period = editorial_date("Europe/Zurich")
    bucket = await db["budget_buckets"].find_one({"bucket_key": "global_audio", "period_start": period})
    if not bucket:
        return True
    reserved = bucket.get("reserved_microunits", 0) + bucket.get("spent_microunits", 0)
    return reserved < bucket.get("limit_microunits", settings.audio_daily_global_cap_microunits)
