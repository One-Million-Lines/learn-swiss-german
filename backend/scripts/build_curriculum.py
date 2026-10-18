"""Build the introductory curriculum release (CLI wrapper)."""
from __future__ import annotations

import json
import sys

from pymongo import MongoClient

sys.path.insert(0, ".")

from app.config import get_settings  # noqa: E402
from app.learning.curriculum_build import build, validate_release  # noqa: E402


def main() -> int:
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, uuidRepresentation="standard", tz_aware=True)
    db = client[settings.mongodb_database]

    results = []
    for dialect_id in ("gsw-zh",):  # Bern release is future work (see TODO)
        summary = build(db, dialect_id)
        release = db["curriculum_releases"].find_one({"_id": summary["release_id"]})
        errors = validate_release(release)
        summary["validation_errors"] = errors
        results.append(summary)

    print(json.dumps(results, indent=2))
    if any(r["validation_errors"] for r in results):
        print("Validation FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
