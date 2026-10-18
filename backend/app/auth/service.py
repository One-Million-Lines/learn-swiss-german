"""Magic-link authentication service (spec 02 §2)."""
from __future__ import annotations

from datetime import timedelta
from typing import Optional

from app.auth import rate_limit, sessions
from app.auth.email_adapter import get_email_adapter
from app.common import tracing
from app.common.errors import bad_request, conflict
from app.common.ids import new_id, deterministic_id
from app.common.security import normalize_email, random_token, sha256_hex, mask_email
from app.common.timeutil import utcnow
from app.config import get_settings
from app.db.client import get_db
from app.db.tx import in_transaction

DEFAULT_PREFERENCES = {
    "support_language": "en",
    "ui_language": "en",
    "active_dialect_id": "gsw-zh",
    "timezone": "Europe/Zurich",
    "daily_goal_minutes": 10,
    "goal": None,
}


async def request_magic_link(
    email: str, *, return_path: str, client_type: str = "web",
    ip: str = "0.0.0.0",
) -> None:
    """Issue a magic link. Always behaves identically whether or not the email
    exists (generic 202 at the router). Throttled per email/IP/client."""
    settings = get_settings()
    normalized = normalize_email(email)
    if "@" not in normalized:
        raise bad_request("A valid email address is required.", "INVALID_EMAIL")

    if return_path not in settings.allowed_return_paths:
        raise bad_request("Return path is not allowed.", "INVALID_RETURN_PATH")

    # Throttles (spec defaults): 5/email/hour, 20/IP/hour, burst 3/IP/minute.
    allowed = (
        await rate_limit.check_and_increment(f"magic:email:{normalized}", limit=5, window_seconds=3600)
        and await rate_limit.check_and_increment(f"magic:ip:{ip}", limit=20, window_seconds=3600)
        and await rate_limit.check_and_increment(f"magic:ipburst:{ip}", limit=3, window_seconds=60)
    )
    if not allowed:
        # Do not reveal account existence; silently drop beyond the limit.
        tracing.warning("magic_link_throttled", email=mask_email(normalized))
        return

    db = get_db()
    token = random_token(32)
    challenge = {
        "_id": new_id(),
        "schema_version": 1,
        "token_hash": sha256_hex(token),
        "purpose": "login",
        "email_normalized": normalized,
        "state": "pending",
        "client_type": client_type,
        "return_path": return_path,
        "user_id": None,
        "new_email": None,
        "consumed_at": None,
        "expires_at": utcnow() + timedelta(seconds=settings.magic_link_ttl_seconds),
        "created_at": utcnow(),
    }
    await db["auth_challenges"].insert_one(challenge)

    # Token travels in the URL fragment; the SPA exchanges it via POST.
    link = f"{settings.public_web_base_url}{return_path}#token={token}"
    await get_email_adapter().send_magic_link(to_email=normalized, link=link, purpose="login")


async def consume_magic_link(token: str, *, client_type: str = "web") -> dict:
    """Atomically consume a pending challenge and create a session."""
    db = get_db()
    now = utcnow()
    token_hash = sha256_hex(token)

    challenge = await db["auth_challenges"].find_one({"token_hash": token_hash})
    if not challenge or challenge.get("state") != "pending":
        raise conflict("This link is invalid or already used.", "LINK_INVALID")
    if challenge["expires_at"] <= now:
        raise conflict("This link has expired.", "LINK_EXPIRED")

    normalized = challenge["email_normalized"]

    created = {"user": None}

    async def _txn(s):
        # Consume the challenge only if it is still pending (atomic guard).
        updated = await db["auth_challenges"].update_one(
            {"_id": challenge["_id"], "state": "pending"},
            {"$set": {"state": "consumed", "consumed_at": now}},
            session=s,
        )
        if updated.modified_count != 1:
            raise conflict("This link is invalid or already used.", "LINK_INVALID")

        user = await db["users"].find_one({"email_normalized": normalized}, session=s)
        if user is None:
            user_id = new_id()
            user = {
                "_id": user_id,
                "schema_version": 1,
                "email_normalized": normalized,
                "email_verified_at": now,
                "display_name": None,
                "roles": [],  # new users never receive elevated roles
                "status": "active",
                "onboarding": {"completed": False},
                "preferences": dict(DEFAULT_PREFERENCES),
                "created_at": now,
                "updated_at": now,
                "version": 1,
            }
            await db["users"].insert_one(user, session=s)
            await db["auth_identities"].insert_one(
                {
                    "_id": deterministic_id("identity", "email", "swissspeak", normalized),
                    "user_id": user_id,
                    "provider": "email",
                    "issuer": "swissspeak",
                    "subject": normalized,
                    "email_snapshot": normalized,
                    "verified": True,
                    "linked_at": now,
                    "created_at": now,
                },
                session=s,
            )
        else:
            if user.get("status") != "active":
                raise conflict("Account is not active.", "ACCOUNT_INACTIVE")
        created["user"] = user

    await in_transaction(_txn)
    user = created["user"]
    user_id = user["_id"]

    # Session creation outside the challenge transaction (its own atomic insert).
    creds = await sessions.create_session(user_id, client_type=client_type)
    tracing.info("magic_link_consumed", user_id=user_id)
    return {"user": user, "credentials": creds}


async def get_user(user_id: str) -> Optional[dict]:
    return await get_db()["users"].find_one({"_id": user_id})
