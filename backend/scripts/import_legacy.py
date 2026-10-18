"""CLI wrapper for the legacy JSON migration.

Usage::

    python -m scripts.import_legacy --dry-run
    python -m scripts.import_legacy --apply
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from pymongo import MongoClient

sys.path.insert(0, ".")

from app.config import get_settings  # noqa: E402
from app.content.migrate import run_migration  # noqa: E402

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data-json"))


def main() -> int:
    parser = argparse.ArgumentParser(description="SwissSpeak legacy migration")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="report without writing")
    group.add_argument("--apply", action="store_true", help="write to MongoDB")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--database", default=None)
    args = parser.parse_args()

    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, uuidRepresentation="standard", tz_aware=True)
    db = client[args.database or settings.mongodb_database]

    report = run_migration(db, args.data_dir, apply=args.apply)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["conflicts"]:
        print(f"\nFAIL: {len(report['conflicts'])} legacy-id conflict(s).", file=sys.stderr)
        return 1

    if args.apply:
        sc, pc = report["source_counts"], report.get("persisted_counts", {})
        ok = (
            pc.get("content_items", 0)
            >= sc["topics"] + sc["subtopics"] + sc["dialogues"] + sc["patterns"] + sc["vocabulary_groups"]
        )
        print("\nReconciliation:", "OK" if ok else "MISMATCH")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
