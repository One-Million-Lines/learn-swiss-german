"""One-time admin bootstrap (spec setup runbook step 4).

Grants administrator + publisher + editor roles to an operator-chosen email.
The user must sign in at least once (so the account exists) OR is created here
with a verified email identity. Audited. Remove/avoid re-running in production.

Usage::

    python -m scripts.bootstrap_admin --email you@example.com
"""
from __future__ import annotations

import argparse
import sys

from pymongo import MongoClient

sys.path.insert(0, ".")

from app.common.ids import deterministic_id, new_id  # noqa: E402
from app.common.security import normalize_email  # noqa: E402
from app.common.timeutil import utcnow  # noqa: E402
from app.config import get_settings  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap the first administrator")
    parser.add_argument("--email", required=True)
    args = parser.parse_args()

    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, uuidRepresentation="standard", tz_aware=True)
    db = client[settings.mongodb_database]
    now = utcnow()
    email = normalize_email(args.email)

    roles = ["administrator", "publisher", "editor"]
    user = db["users"].find_one({"email_normalized": email})
    if user is None:
        user_id = new_id()
        db["users"].insert_one({
            "_id": user_id, "schema_version": 1, "email_normalized": email,
            "email_verified_at": now, "display_name": "Administrator", "roles": roles,
            "status": "active", "onboarding": {"completed": True},
            "preferences": {"support_language": "en", "ui_language": "en",
                            "active_dialect_id": "gsw-zh", "timezone": "Europe/Zurich",
                            "daily_goal_minutes": 10, "goal": None},
            "created_at": now, "updated_at": now, "version": 1,
        })
        db["auth_identities"].replace_one(
            {"_id": deterministic_id("identity", "email", "swissspeak", email)},
            {"_id": deterministic_id("identity", "email", "swissspeak", email),
             "user_id": user_id, "provider": "email", "issuer": "swissspeak",
             "subject": email, "email_snapshot": email, "verified": True,
             "linked_at": now, "created_at": now}, upsert=True)
    else:
        user_id = user["_id"]
        db["users"].update_one({"_id": user_id},
                               {"$set": {"roles": roles, "updated_at": now}, "$inc": {"version": 1}})

    db["audit_log"].insert_one({
        "_id": new_id(), "actor_user_id": None, "actor_system": "bootstrap_admin",
        "action": "user.bootstrap_admin", "target_type": "user", "target_id": user_id,
        "reason": "one-time admin bootstrap", "created_at": now,
    })
    print(f"Granted {roles} to {email}. Sign in with a magic link to use the admin API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
