"""Audit logging — every admin write emits a record (spec 01 §8)."""
from __future__ import annotations

from typing import Optional

from app.common import tracing
from app.common.ids import new_id
from app.common.timeutil import utcnow
from app.db.client import get_db


async def record(*, actor_user_id: Optional[str], action: str, target_type: str,
                 target_id: str, reason: Optional[str] = None,
                 before_ref: Optional[dict] = None, after_ref: Optional[dict] = None) -> None:
    await get_db()["audit_log"].insert_one({
        "_id": new_id(),
        "actor_user_id": actor_user_id,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "before_ref": before_ref,
        "after_ref": after_ref,
        "reason": reason,
        "request_id": tracing.get_request_id(),
        "created_at": utcnow(),
    })
