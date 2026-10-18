"""Read access to published versioned app configuration."""
from __future__ import annotations

from typing import Any, Optional

from app.db.client import get_db


async def get_published_config(key: str) -> Optional[dict]:
    db = get_db()
    head = await db["config_heads"].find_one({"_id": key})
    if not head:
        return None
    revision = head.get("published_revision")
    doc = await db["app_config"].find_one({"key": key, "revision": revision})
    return doc.get("payload") if doc else None


async def config_value(key: str, default: Any = None) -> Any:
    payload = await get_published_config(key)
    return payload if payload is not None else default
