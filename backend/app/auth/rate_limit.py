"""MongoDB-backed fixed-window rate limiting with TTL cleanup."""
from __future__ import annotations

from datetime import timedelta

from app.common.ids import deterministic_id
from app.common.timeutil import utcnow
from app.db.client import get_db


async def check_and_increment(bucket_key: str, *, limit: int, window_seconds: int) -> bool:
    """Atomically increment the current window counter. Returns True if allowed.

    The counter is bounded per (bucket_key, window_start) and expires via TTL.
    Enforcement is server-side; this never reveals account existence.
    """
    db = get_db()
    now = utcnow()
    window_start = now.replace(microsecond=0)
    # Align window_start to the window boundary.
    epoch = int(window_start.timestamp())
    aligned = epoch - (epoch % window_seconds)
    from datetime import datetime, timezone

    window_dt = datetime.fromtimestamp(aligned, tz=timezone.utc)
    _id = deterministic_id("ratelimit", bucket_key, str(aligned))
    expires_at = window_dt + timedelta(seconds=window_seconds * 2)

    result = await db["rate_limit_buckets"].find_one_and_update(
        {"_id": _id},
        {
            "$inc": {"count": 1},
            "$setOnInsert": {
                "bucket_key": bucket_key,
                "window_start": window_dt,
                "expires_at": expires_at,
            },
        },
        upsert=True,
        return_document=True,
    )
    return result.get("count", 1) <= limit
