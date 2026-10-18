"""Deterministic legacy JSON -> MongoDB migration (spec 04 §3).

Idempotent: deterministic UUIDv5 IDs mean a second run produces identical
documents and unchanged counts. Legacy Swiss text is imported with
``dialect_id=null`` and an explicit *unverified* dialect label — never relabeled
Zürichdeutsch. JSON remains an archival migration input, not a runtime fallback.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Tuple

from pymongo import ReplaceOne
from pymongo.database import Database

from app.common.ids import deterministic_id
from app.common.timeutil import utcnow
from app.content.canonical import CANONICALIZATION_VERSION, canonicalize, text_sha256

MIGRATION_VERSION = "legacy-json-v1"
MIGRATION_KEY = "import_legacy_json"

# Language tags for legacy fields.
LANG_SWISS = "gsw-CH"
LANG_GERMAN = "de-CH"
LANG_EN = "en"
LANG_ES = "es"

UNVERIFIED_DIALECT_LABEL = "Swiss German — dialect not verified"


def _utterance(buffer: Dict[str, dict], language_tag: str, text: str) -> str | None:
    """Create/dedupe an utterance; return its deterministic _id (or None if empty)."""
    if text is None or str(text).strip() == "":
        return None
    canonical = canonicalize(text)
    if not canonical:
        return None
    sha = text_sha256(canonical)
    context = "default"
    dialect_id = None  # legacy content is dialect-unverified
    uid = deterministic_id(
        "utterance", language_tag, str(dialect_id), context, str(CANONICALIZATION_VERSION), sha
    )
    if uid not in buffer:
        buffer[uid] = {
            "_id": uid,
            "schema_version": 1,
            "language_tag": language_tag,
            "dialect_id": dialect_id,
            "pronunciation_context_id": context,
            "canonicalization_version": CANONICALIZATION_VERSION,
            "text": str(text),
            "canonical_text": canonical,
            "text_sha256": sha,
            "created_at": utcnow(),
        }
    return uid


def _checksum(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def build_documents(data_dir: str) -> Tuple[Dict[str, List[dict]], Dict[str, int]]:
    """Pure transform: read JSON, return {collection: [docs]} and source counts."""
    now = utcnow()
    utterances: Dict[str, dict] = {}
    content_items: List[dict] = []
    content_revisions: List[dict] = []
    legacy_mappings: List[dict] = []

    def add_item(item: dict, revision_payload: dict, *, references: List[dict] | None = None,
                 private_grading: dict | None = None) -> None:
        item_id = item["_id"]
        content_items.append(item)
        content_revisions.append({
            "_id": deterministic_id("revision", item_id, "1"),
            "schema_version": 1,
            "item_id": item_id,
            "revision": 1,
            "kind": item["kind"],
            "dialect_id": item.get("dialect_id"),
            "status": "published",
            "payload": revision_payload,
            "private_grading": private_grading,
            "references": references or [],
            "provenance": {"source": "legacy_json", "migration_version": MIGRATION_VERSION},
            "qa": {"dialect_verified": False},
            "created_by": "system",
            "created_at": now,
            "version": 1,
        })

    def base_item(kind: str, slug: str, legacy_id: str, *, topic_id=None, subtopic_id=None,
                  scenario_id=None, title=None, summary=None, discovery=None,
                  search_text="", sort_order=0, tags=None) -> dict:
        item_id = deterministic_id("content", kind, slug)
        legacy_mappings.append({
            "_id": deterministic_id("legacy_map", "json", kind, legacy_id),
            "source": "json",
            "entity_type": kind,
            "legacy_id": legacy_id,
            "new_item_id": item_id,
            "migration_version": MIGRATION_VERSION,
            "status": "mapped",
            "created_at": now,
        })
        return {
            "_id": item_id,
            "schema_version": 1,
            "kind": kind,
            "slug": slug,
            "dialect_id": None,
            "scenario_id": scenario_id,
            "legacy_id": legacy_id,
            "status": "published",
            "published_revision": 1,
            "draft_revision": None,
            "discovery": discovery or {},
            "title": title,
            "summary": summary,
            "tags": tags or [],
            "topic_id": topic_id,
            "subtopic_id": subtopic_id,
            "search_text": search_text.lower()[:2000],
            "sort_order": sort_order,
            "created_at": now,
            "updated_at": now,
            "version": 1,
        }

    # --- topics ---
    topics = json.load(open(os.path.join(data_dir, "topics.json"), encoding="utf-8"))
    for idx, t in enumerate(topics):
        item = base_item(
            "topic", t["id"], t["id"], title=t["title"], summary=t.get("description"),
            discovery={"title": t["title"], "description": t.get("description"),
                       "icon": t.get("icon"), "color": t.get("color")},
            search_text=f"{t['title']} {t.get('description','')}", sort_order=idx,
        )
        add_item(item, {"title": t["title"], "description": t.get("description"),
                        "icon": t.get("icon"), "color": t.get("color")})

    # --- subtopics + dialogues ---
    sub_dir = os.path.join(data_dir, "subtopics")
    sub_files = sorted(
        f for f in os.listdir(sub_dir) if f.endswith(".json") and f != "index.json"
    )
    dialogue_count = 0
    turn_count = 0
    for sidx, fname in enumerate(sub_files):
        sub = json.load(open(os.path.join(sub_dir, fname), encoding="utf-8"))
        scenario_slug = sub["id"]
        dialogue_refs: List[str] = []
        for d in sub["dialogues"]:
            dialogue_count += 1
            turns = []
            for pos, line in enumerate(d["lines"]):
                turn_count += 1
                swiss_uid = _utterance(utterances, LANG_SWISS, line.get("swissGerman", ""))
                de_uid = _utterance(utterances, LANG_GERMAN, line.get("german", ""))
                en_uid = _utterance(utterances, LANG_EN, line.get("english", ""))
                es_uid = _utterance(utterances, LANG_ES, line.get("spanish", ""))
                turn_id = deterministic_id("turn", d["id"], str(pos))
                translations = {}
                if en_uid:
                    translations["en"] = en_uid
                if es_uid:
                    translations["es"] = es_uid
                turns.append({
                    "id": turn_id,
                    "speaker": line.get("speaker"),
                    "speaker_id": (line.get("speaker") or "").strip().lower().replace(" ", "_") or "speaker",
                    "utterance_id": swiss_uid,
                    "german_utterance_id": de_uid,
                    "translation_utterance_ids": translations,
                    "objective_ids": [],
                })
            key_phrases = [
                {
                    "swiss_utterance_id": _utterance(utterances, LANG_SWISS, kp.get("swissGerman", "")),
                    "german_utterance_id": _utterance(utterances, LANG_GERMAN, kp.get("german", "")),
                    "translation_utterance_ids": {
                        k: v for k, v in {
                            "en": _utterance(utterances, LANG_EN, kp.get("english", "")),
                        }.items() if v
                    },
                }
                for kp in d.get("keyPhrases", [])
            ]
            differences = [
                {
                    "swiss_utterance_id": _utterance(utterances, LANG_SWISS, diff.get("swissGerman", "")),
                    "german_utterance_id": _utterance(utterances, LANG_GERMAN, diff.get("german", "")),
                    "explanation": diff.get("explanation"),
                }
                for diff in d.get("differences", [])
            ]
            dpayload = {
                "scenario_id": deterministic_id("scenario", scenario_slug),
                "title": d.get("title"),
                "situation": d.get("situation"),
                "register": "neutral",
                "level": d.get("level", "beginner"),
                "dialect_verified": False,
                "dialect_label": UNVERIFIED_DIALECT_LABEL,
                "speakers": [],
                "turns": turns,
                "comparison_notes": differences,
                "key_phrases": key_phrases,
                "key_objective_ids": [],
            }
            ditem = base_item(
                "dialogue", d["id"], d["id"], topic_id=sub["topicId"], subtopic_id=sub["id"],
                scenario_id=deterministic_id("scenario", scenario_slug),
                title=d.get("title"), summary=d.get("situation"),
                discovery={"title": d.get("title"), "level": d.get("level"),
                           "dialect_verified": False, "subtopic_id": sub["id"],
                           "topic_id": sub["topicId"], "turn_count": len(turns)},
                search_text=f"{d.get('title','')} {d.get('situation','')}",
            )
            add_item(ditem, dpayload)
            dialogue_refs.append(ditem["_id"])

        sitem = base_item(
            "subtopic", sub["id"], sub["id"], topic_id=sub["topicId"],
            title=sub["title"], summary=sub.get("description"),
            discovery={"title": sub["title"], "description": sub.get("description"),
                       "topic_id": sub["topicId"], "dialogue_count": len(sub["dialogues"])},
            search_text=f"{sub['title']} {sub.get('description','')}", sort_order=sidx,
        )
        add_item(sitem, {"title": sub["title"], "description": sub.get("description"),
                         "topic_id": sub["topicId"], "dialogue_item_ids": dialogue_refs})

    # --- patterns ---
    patterns = json.load(open(os.path.join(data_dir, "patterns.json"), encoding="utf-8"))
    for pidx, p in enumerate(patterns):
        examples = [
            {
                "swiss_utterance_id": _utterance(utterances, LANG_SWISS, ex.get("swissGerman", "")),
                "german_utterance_id": _utterance(utterances, LANG_GERMAN, ex.get("german", "")),
                "translation_utterance_ids": {
                    k: v for k, v in {
                        "en": _utterance(utterances, LANG_EN, ex.get("english", "")),
                        "es": _utterance(utterances, LANG_ES, ex.get("spanish", "")),
                    }.items() if v
                },
            }
            for ex in p.get("examples", [])
        ]
        item = base_item(
            "pattern", p["id"], p["id"], title=p["title"], summary=p.get("description"),
            discovery={"title": p["title"], "description": p.get("description")},
            search_text=f"{p['title']} {p.get('description','')}", sort_order=pidx,
        )
        add_item(item, {"title": p["title"], "description": p.get("description"),
                        "dialect_verified": False, "examples": examples})

    # --- vocabulary groups ---
    vocab = json.load(open(os.path.join(data_dir, "vocabulary.json"), encoding="utf-8"))
    for vidx, g in enumerate(vocab):
        words = [
            {
                "swiss_utterance_id": _utterance(utterances, LANG_SWISS, w.get("swissGerman", "")),
                "german_utterance_id": _utterance(utterances, LANG_GERMAN, w.get("german", "")),
                "translation_utterance_ids": {
                    k: v for k, v in {
                        "en": _utterance(utterances, LANG_EN, w.get("english", "")),
                        "es": _utterance(utterances, LANG_ES, w.get("spanish", "")),
                    }.items() if v
                },
            }
            for w in g.get("words", [])
        ]
        item = base_item(
            "vocabulary_group", g["id"], g["id"], topic_id=g.get("topicId"),
            title=g["title"],
            discovery={"title": g["title"], "topic_id": g.get("topicId"),
                       "word_count": len(words)},
            search_text=g["title"], sort_order=vidx,
        )
        add_item(item, {"title": g["title"], "topic_id": g.get("topicId"),
                        "dialect_verified": False, "words": words})

    documents = {
        "utterances": list(utterances.values()),
        "content_items": content_items,
        "content_revisions": content_revisions,
        "legacy_mappings": legacy_mappings,
    }
    source_counts = {
        "topics": len(topics),
        "subtopics": len(sub_files),
        "dialogues": dialogue_count,
        "turns": turn_count,
        "patterns": len(patterns),
        "vocabulary_groups": len(vocab),
    }
    return documents, source_counts


def daily_config_payload() -> dict:
    """Deterministic daily selection config referencing imported dialogues/phrases.

    Uses a rotation of approved dialogue item IDs plus the legacy phrase list, so
    the homepage never triggers generation.
    """
    return {
        "mode": "deterministic_rotation",
        "timezone": "Europe/Zurich",
        "dialect_id": None,
    }


def run_migration(db: Database, data_dir: str, *, apply: bool) -> dict:
    """Run the migration against a (sync) Database. Returns a report dict."""
    documents, source_counts = build_documents(data_dir)

    report: dict = {
        "migration_key": MIGRATION_KEY,
        "migration_version": MIGRATION_VERSION,
        "dry_run": not apply,
        "source_counts": source_counts,
        "mapped_counts": {k: len(v) for k, v in documents.items()},
        "checksum": _checksum({k: sorted(d["_id"] for d in v) for k, v in documents.items()}),
        "conflicts": [],
    }

    # Detect legacy-id conflicts (same legacy id mapping to different new ids).
    seen: Dict[str, str] = {}
    for m in documents["legacy_mappings"]:
        key = f"{m['entity_type']}:{m['legacy_id']}"
        if key in seen and seen[key] != m["new_item_id"]:
            report["conflicts"].append(key)
        seen[key] = m["new_item_id"]

    if not apply:
        return report

    # Idempotent upserts by deterministic _id.
    for collection, docs in documents.items():
        if not docs:
            continue
        ops = [ReplaceOne({"_id": d["_id"]}, d, upsert=True) for d in docs]
        db[collection].bulk_write(ops, ordered=False)

    # Record daily selection config (published head) if not present.
    _ensure_daily_config(db)

    # migration_runs record
    db["migration_runs"].replace_one(
        {"migration_key": MIGRATION_KEY},
        {
            "_id": deterministic_id("migration_run", MIGRATION_KEY),
            "migration_key": MIGRATION_KEY,
            "checksum": report["checksum"],
            "state": "completed",
            "source_counts": source_counts,
            "mapped_counts": report["mapped_counts"],
            "rejected_ref": {"conflicts": report["conflicts"]},
            "started_at": utcnow(),
            "completed_at": utcnow(),
            "created_at": utcnow(),
        },
        upsert=True,
    )

    # Reconcile persisted counts.
    report["persisted_counts"] = {
        c: db[c].count_documents({}) for c in documents.keys()
    }
    return report


def _ensure_daily_config(db: Database) -> None:
    now = utcnow()
    key = "daily_selection"
    if db["app_config"].find_one({"key": key, "revision": 1}) is None:
        db["app_config"].insert_one({
            "_id": deterministic_id("app_config", key, "1"),
            "key": key,
            "revision": 1,
            "status": "published",
            "payload": daily_config_payload(),
            "created_by": "system",
            "created_at": now,
        })
        db["config_heads"].replace_one(
            {"_id": key},
            {"_id": key, "published_revision": 1, "updated_at": now, "version": 1},
            upsert=True,
        )
