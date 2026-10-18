"""Serialization helpers: BSON/datetime -> JSON-safe, private-field stripping."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId


def jsonable(value: Any) -> Any:
    """Recursively convert datetimes/ObjectIds to JSON-safe primitives."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


# Fields that must never leave the server in public/learner responses.
_PRIVATE_KEYS = {"private_grading", "token_hash", "access_hash", "refresh_hash",
                 "csrf_hash", "used_refresh_hashes", "code_hash", "prompt_ref"}


def public(doc: dict | None) -> dict | None:
    if doc is None:
        return None
    return jsonable({k: v for k, v in doc.items() if k not in _PRIVATE_KEYS})
