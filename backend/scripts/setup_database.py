"""Idempotent MongoDB setup: collections, JSON Schema validators, named indexes.

Usage::

    python -m scripts.setup_database --apply       # create/retrofit everything
    python -m scripts.setup_database --check        # verify, non-zero exit on drift

Guards: never drops the database and never drops indexes automatically. Index
changes in production require an explicit, reviewed migration.
"""
from __future__ import annotations

import argparse
import json
import sys

from pymongo import MongoClient

# Allow running as a script from the backend/ directory.
sys.path.insert(0, ".")

from app.config import get_settings  # noqa: E402
from app.db.schema import ALL_COLLECTIONS, INDEXES, VALIDATORS  # noqa: E402


def _validator_doc(collection: str):
    schema = VALIDATORS.get(collection)
    if not schema:
        return None
    return {"$jsonSchema": schema}


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _current_validator(db, name: str):
    try:
        info = db.command("listCollections", filter={"name": name})
        batch = info.get("cursor", {}).get("firstBatch", [])
        if batch:
            return batch[0].get("options", {}).get("validator")
    except Exception:
        pass
    return None


def _ensure_collection(db, name: str, apply: bool) -> list[str]:
    changes: list[str] = []
    existing = db.list_collection_names()
    validator = _validator_doc(name)
    if name not in existing:
        changes.append(f"create collection {name}")
        if apply:
            opts = {}
            if validator:
                opts = {
                    "validator": validator,
                    "validationLevel": "strict",
                    "validationAction": "error",
                }
            db.create_collection(name, **opts)
    elif validator:
        # Only a *difference* in the stored validator counts as drift.
        current = _current_validator(db, name)
        if _canonical(current) != _canonical(validator):
            changes.append(f"collMod validator {name}")
            if apply:
                db.command(
                    {
                        "collMod": name,
                        "validator": validator,
                        "validationLevel": "strict",
                        "validationAction": "error",
                    }
                )
    return changes


def _ensure_indexes(db, apply: bool) -> list[str]:
    changes: list[str] = []
    for collection, keys, name, options in INDEXES:
        coll = db[collection]
        try:
            existing = {ix["name"]: ix for ix in coll.list_indexes()}
        except Exception:
            existing = {}
        if name not in existing:
            changes.append(f"create index {collection}.{name}")
            if apply:
                coll.create_index(list(keys.items()), name=name, **options)
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description="SwissSpeak database setup")
    parser.add_argument("--apply", action="store_true", help="apply changes")
    parser.add_argument("--check", action="store_true", help="report drift only (exit 1 if any)")
    parser.add_argument("--database", default=None, help="override target database")
    args = parser.parse_args()

    settings = get_settings()
    database = args.database or settings.mongodb_database
    client = MongoClient(settings.mongodb_uri, uuidRepresentation="standard", tz_aware=True)
    db = client[database]

    apply = args.apply and not args.check
    all_changes: list[str] = []

    for collection in ALL_COLLECTIONS:
        all_changes += _ensure_collection(db, collection, apply)
    all_changes += _ensure_indexes(db, apply)

    if args.check:
        if all_changes:
            print(f"DRIFT detected in '{database}' ({len(all_changes)} item(s)):")
            for c in all_changes:
                print("  -", c)
            return 1
        print(f"OK: database '{database}' matches the manifest ({len(ALL_COLLECTIONS)} collections, {len(INDEXES)} indexes).")
        return 0

    if apply:
        if all_changes:
            print(f"Applied {len(all_changes)} change(s) to '{database}':")
            for c in all_changes:
                print("  +", c)
        else:
            print(f"No changes needed. '{database}' already matches the manifest.")
        return 0

    print("Nothing to do. Pass --apply to create or --check to verify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
