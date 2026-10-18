"""Canonical database manifest: collections, indexes and JSON Schema validators.

This is the single source of truth encoded from `docs/specification/03`.
`scripts/setup_database.py` consumes it with `--check` / `--apply`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

# --------------------------------------------------------------------------- #
# Index manifest: (collection, key_doc, index_name, options)                   #
# --------------------------------------------------------------------------- #
IndexSpec = Tuple[str, Dict[str, int], str, Dict[str, Any]]

TTL = {"expireAfterSeconds": 0}
UNIQUE = {"unique": True}


def _ttl(collection: str) -> IndexSpec:
    return (collection, {"expires_at": 1}, "ttl_expires_at", {"expireAfterSeconds": 0})


INDEXES: List[IndexSpec] = [
    # Identity & administration
    ("users", {"email_normalized": 1}, "u_email", UNIQUE),
    ("auth_identities", {"provider": 1, "issuer": 1, "subject": 1}, "u_identity", UNIQUE),
    ("auth_identities", {"user_id": 1}, "by_user", {}),
    ("auth_challenges", {"token_hash": 1}, "u_token", UNIQUE),
    _ttl("auth_challenges"),
    ("sessions", {"access_hash": 1}, "u_access", UNIQUE),
    ("sessions", {"refresh_hash": 1}, "u_refresh", UNIQUE),
    ("sessions", {"family_id": 1}, "u_family", UNIQUE),
    ("sessions", {"user_id": 1, "revoked_at": 1}, "by_user_revoked", {}),
    _ttl("sessions"),
    ("native_auth_codes", {"code_hash": 1}, "u_code", UNIQUE),
    _ttl("native_auth_codes"),
    ("rate_limit_buckets", {"bucket_key": 1, "window_start": 1}, "u_bucket", UNIQUE),
    _ttl("rate_limit_buckets"),
    ("audit_log", {"target_type": 1, "target_id": 1, "created_at": -1}, "by_target_time", {}),
    ("audit_log", {"actor_user_id": 1, "created_at": -1}, "by_actor_time", {}),
    _ttl("audit_log"),
    # Content & publishing
    ("dialects", {"code": 1}, "u_code", UNIQUE),
    ("content_items", {"kind": 1, "slug": 1}, "u_kind_slug", UNIQUE),
    ("content_items", {"kind": 1, "dialect_id": 1, "status": 1, "updated_at": -1, "_id": 1}, "discover", {}),
    ("content_items", {"topic_id": 1, "kind": 1, "status": 1}, "by_topic", {}),
    ("content_items", {"scenario_id": 1, "kind": 1, "dialect_id": 1}, "scenario_variants", {}),
    ("content_revisions", {"item_id": 1, "revision": 1}, "u_item_revision", UNIQUE),
    ("content_revisions", {"status": 1, "kind": 1, "dialect_id": 1, "updated_at": -1}, "review_queue", {}),
    (
        "utterances",
        {"language_tag": 1, "dialect_id": 1, "pronunciation_context_id": 1, "canonicalization_version": 1, "text_sha256": 1},
        "u_utterance",
        UNIQUE,
    ),
    ("curriculum_releases", {"curriculum_key": 1, "dialect_id": 1, "release_number": 1}, "u_release", UNIQUE),
    ("curriculum_releases", {"dialect_id": 1, "status": 1, "release_number": -1}, "available_releases", {}),
    ("app_config", {"key": 1, "revision": 1}, "u_key_revision", UNIQUE),
    ("app_config", {"key": 1, "status": 1}, "config_status", {}),
    ("config_heads", {"published_revision": 1}, "head_rev", {}),
    ("legacy_mappings", {"source": 1, "entity_type": 1, "legacy_id": 1}, "u_legacy", UNIQUE),
    # Learner records
    ("enrollments", {"user_id": 1, "curriculum_key": 1, "dialect_id": 1}, "u_enrollment", UNIQUE),
    ("enrollments", {"user_id": 1, "status": 1}, "user_enrollments", {}),
    ("attempts", {"user_id": 1, "submitted_at": -1, "_id": 1}, "user_history", {}),
    ("attempts", {"user_id": 1, "state": 1, "started_at": -1}, "resume_attempts", {}),
    ("attempts", {"enrollment_id": 1, "node_id": 1}, "node_attempts", {}),
    ("node_progress", {"enrollment_id": 1, "node_id": 1}, "u_node_progress", UNIQUE),
    ("objective_progress", {"user_id": 1, "dialect_id": 1, "objective_id": 1}, "u_objective_progress", UNIQUE),
    ("objective_progress", {"user_id": 1, "dialect_id": 1, "due_at": 1, "_id": 1}, "due_reviews", {}),
    ("reward_ledger", {"user_id": 1, "source_key": 1}, "u_reward_source", UNIQUE),
    ("reward_ledger", {"user_id": 1, "created_at": -1}, "reward_history", {}),
    ("activity_days", {"user_id": 1, "local_date": 1}, "u_activity_day", UNIQUE),
    ("bookmarks", {"user_id": 1, "target_type": 1, "target_id": 1, "dialect_id": 1}, "u_bookmark", UNIQUE),
    ("bookmarks", {"user_id": 1, "created_at": -1, "_id": 1}, "user_bookmarks", {}),
    ("idempotency_receipts", {"user_id": 1, "scope": 1, "key": 1}, "u_idempotency", UNIQUE),
    _ttl("idempotency_receipts"),
    # AI, audio, creators, operations
    ("media_assets", {"audio_key": 1}, "u_audio_key", {"unique": True, "partialFilterExpression": {"audio_key": {"$type": "string"}}}),
    ("media_assets", {"utterance_id": 1, "status": 1}, "utterance_audio", {}),
    ("media_assets", {"status": 1, "created_at": 1}, "media_operations", {}),
    ("jobs", {"dedupe_key": 1}, "u_job_dedupe", UNIQUE),
    ("jobs", {"status": 1, "available_at": 1, "_id": 1}, "claim_queue", {}),
    ("jobs", {"status": 1, "lease_until": 1}, "expired_leases", {}),
    _ttl("jobs"),
    ("ai_runs", {"job_id": 1}, "job_runs", {}),
    ("ai_runs", {"purpose": 1, "created_at": -1}, "usage_history", {}),
    ("budget_buckets", {"bucket_key": 1, "period_start": 1}, "u_budget_period", UNIQUE),
    ("budget_reservations", {"request_key": 1}, "u_budget_request", UNIQUE),
    ("budget_reservations", {"state": 1, "created_at": 1}, "unsettled_reservations", {}),
    ("creators", {"slug": 1}, "u_creator_slug", UNIQUE),
    ("creators", {"status": 1, "featured_order": 1, "_id": 1}, "featured_creators", {}),
    ("creator_resources", {"platform": 1, "canonical_url": 1}, "u_platform_url", UNIQUE),
    ("creator_resources", {"creator_id": 1, "status": 1}, "creator_resources", {}),
    ("reports", {"status": 1, "created_at": 1}, "moderation_queue", {}),
    ("reports", {"target_type": 1, "target_id": 1}, "target_reports", {}),
    ("migration_runs", {"migration_key": 1}, "u_migration", UNIQUE),
]

# All application collections (GridFS buckets are created by the driver).
ALL_COLLECTIONS: List[str] = sorted({spec[0] for spec in INDEXES})


# --------------------------------------------------------------------------- #
# JSON Schema validators                                                       #
# --------------------------------------------------------------------------- #
def _obj(required: List[str], properties: Dict[str, Any], additional: bool = True) -> Dict[str, Any]:
    schema: Dict[str, Any] = {
        "bsonType": "object",
        "required": required,
        "properties": properties,
    }
    if not additional:
        schema["additionalProperties"] = False
    return schema


_STR = {"bsonType": "string"}
_STR_NULL = {"bsonType": ["string", "null"]}
_INT1 = {"bsonType": "int", "minimum": 1}
_DATE = {"bsonType": "date"}
_DATE_NULL = {"bsonType": ["date", "null"]}
_SHA = {"bsonType": "string", "pattern": "^[0-9a-f]{64}$"}
_BOOL = {"bsonType": "bool"}


VALIDATORS: Dict[str, Dict[str, Any]] = {
    "users": _obj(
        ["_id", "schema_version", "email_normalized", "roles", "status", "created_at"],
        {
            "_id": _STR,
            "schema_version": _INT1,
            "email_normalized": _STR,
            "email_verified_at": _DATE_NULL,
            "display_name": _STR_NULL,
            "roles": {"bsonType": "array", "items": _STR},
            "status": {"enum": ["active", "suspended", "deleting"]},
            "onboarding": {"bsonType": "object"},
            "preferences": {"bsonType": "object"},
            "created_at": _DATE,
            "updated_at": _DATE,
            "version": {"bsonType": "int"},
        },
    ),
    "auth_identities": _obj(
        ["_id", "user_id", "provider", "issuer", "subject", "created_at"],
        {
            "_id": _STR,
            "user_id": _STR,
            "provider": {"enum": ["email", "google", "microsoft"]},
            "issuer": _STR,
            "subject": _STR,
            "email_snapshot": _STR_NULL,
            "verified": _BOOL,
            "linked_at": _DATE,
            "created_at": _DATE,
        },
    ),
    "auth_challenges": _obj(
        ["_id", "token_hash", "purpose", "email_normalized", "state", "expires_at", "created_at"],
        {
            "_id": _STR,
            "token_hash": _SHA,
            "purpose": {"enum": ["login", "link", "email_change", "account_deletion"]},
            "email_normalized": _STR,
            "state": {"enum": ["pending", "consumed", "expired"]},
            "client_type": _STR,
            "return_path": _STR,
            "user_id": _STR_NULL,
            "new_email": _STR_NULL,
            "consumed_at": _DATE_NULL,
            "expires_at": _DATE,
            "created_at": _DATE,
        },
    ),
    "sessions": _obj(
        ["_id", "user_id", "access_hash", "refresh_hash", "family_id", "expires_at", "created_at"],
        {
            "_id": _STR,
            "user_id": _STR,
            "access_hash": _SHA,
            "access_expires_at": _DATE,
            "refresh_hash": _SHA,
            "refresh_expires_at": _DATE,
            "used_refresh_hashes": {"bsonType": "array", "items": _SHA},
            "family_id": _STR,
            "client_type": _STR,
            "csrf_hash": _SHA,
            "created_at": _DATE,
            "last_seen_at": _DATE,
            "recent_auth_at": _DATE,
            "revoked_at": _DATE_NULL,
            "expires_at": _DATE,
        },
    ),
    "native_auth_codes": _obj(
        ["_id", "code_hash", "user_id", "expires_at"],
        {"_id": _STR, "code_hash": _SHA, "user_id": _STR, "client_id": _STR,
         "pkce_challenge": _STR, "pkce_method": _STR, "redirect_uri": _STR,
         "consumed_at": _DATE_NULL, "expires_at": _DATE},
    ),
    "rate_limit_buckets": _obj(
        ["_id", "bucket_key", "window_start", "count", "expires_at"],
        {"_id": _STR, "bucket_key": _STR, "window_start": _DATE,
         "count": {"bsonType": "int"}, "expires_at": _DATE},
    ),
    "audit_log": _obj(
        ["_id", "action", "created_at"],
        {"_id": _STR, "actor_user_id": _STR_NULL, "actor_system": _STR_NULL,
         "action": _STR, "target_type": _STR_NULL, "target_id": _STR_NULL,
         "before_ref": {"bsonType": ["object", "null"]}, "after_ref": {"bsonType": ["object", "null"]},
         "reason": _STR_NULL, "request_id": _STR_NULL, "created_at": _DATE,
         "expires_at": _DATE_NULL},
    ),
    "dialects": _obj(
        ["_id", "code", "labels", "language_tag", "status", "created_at"],
        {"_id": _STR, "code": _STR, "labels": {"bsonType": "object"},
         "description": {"bsonType": "object"}, "regional_variety": _STR_NULL,
         "language_tag": _STR, "status": {"enum": ["enabled", "coming_soon", "disabled"]},
         "spelling_guide_ref": {"bsonType": ["object", "null"]},
         "voice_profile_ref": {"bsonType": ["object", "null"]},
         "voice_review_status": _STR_NULL,
         "sources": {"bsonType": "array"}, "sort_order": {"bsonType": "int"},
         "created_at": _DATE, "updated_at": _DATE, "version": {"bsonType": "int"}},
    ),
    "content_items": _obj(
        ["_id", "schema_version", "kind", "slug", "status", "created_at"],
        {"_id": _STR, "schema_version": _INT1, "kind": _STR, "slug": _STR,
         "dialect_id": _STR_NULL, "scenario_id": _STR_NULL, "legacy_id": _STR_NULL,
         "status": {"enum": ["draft", "generated", "in_review", "approved", "published", "archived"]},
         "published_revision": {"bsonType": ["int", "null"]},
         "draft_revision": {"bsonType": ["int", "null"]},
         "discovery": {"bsonType": "object"}, "title": _STR_NULL, "summary": _STR_NULL,
         "tags": {"bsonType": "array"}, "topic_id": _STR_NULL, "subtopic_id": _STR_NULL,
         "search_text": _STR_NULL, "sort_order": {"bsonType": "int"},
         "created_at": _DATE, "updated_at": _DATE, "version": {"bsonType": "int"}},
    ),
    "content_revisions": _obj(
        ["_id", "schema_version", "item_id", "revision", "kind", "status", "payload", "created_at"],
        {"_id": _STR, "schema_version": _INT1, "item_id": _STR, "revision": _INT1,
         "kind": _STR, "dialect_id": _STR_NULL,
         "status": {"enum": ["draft", "generated", "in_review", "approved", "published", "archived", "rejected"]},
         "payload": {"bsonType": "object"}, "private_grading": {"bsonType": ["object", "null"]},
         "references": {"bsonType": "array"}, "provenance": {"bsonType": ["object", "null"]},
         "qa": {"bsonType": ["object", "null"]}, "created_by": _STR_NULL,
         "created_at": _DATE, "updated_at": _DATE_NULL, "version": {"bsonType": "int"}},
    ),
    "utterances": _obj(
        ["_id", "schema_version", "language_tag", "dialect_id", "pronunciation_context_id",
         "canonicalization_version", "text", "canonical_text", "text_sha256", "created_at"],
        {"_id": _STR, "schema_version": _INT1, "language_tag": _STR, "dialect_id": _STR_NULL,
         "pronunciation_context_id": _STR, "canonicalization_version": _INT1,
         "text": {"bsonType": "string", "minLength": 1, "maxLength": 600},
         "canonical_text": {"bsonType": "string", "minLength": 1, "maxLength": 600},
         "text_sha256": _SHA, "created_at": _DATE},
        additional=False,
    ),
    "curriculum_releases": _obj(
        ["_id", "schema_version", "curriculum_key", "dialect_id", "release_number", "status", "nodes", "stages", "created_at"],
        {"_id": _STR, "schema_version": _INT1, "curriculum_key": _STR, "dialect_id": _STR,
         "release_number": _INT1, "status": {"enum": ["draft", "published", "archived"]},
         "nodes": {"bsonType": "array"}, "stages": {"bsonType": "array"},
         "graph_hash": _STR_NULL, "grading_config_ref": {"bsonType": ["object", "null"]},
         "reward_config_ref": {"bsonType": ["object", "null"]},
         "equivalence": {"bsonType": ["object", "null"]}, "published_at": _DATE_NULL,
         "created_at": _DATE, "updated_at": _DATE_NULL, "version": {"bsonType": "int"}},
    ),
    "app_config": _obj(
        ["_id", "key", "revision", "status", "payload", "created_at"],
        {"_id": _STR, "key": _STR, "revision": _INT1,
         "status": {"enum": ["draft", "published", "archived"]},
         "payload": {"bsonType": "object"}, "created_by": _STR_NULL, "created_at": _DATE},
    ),
    "config_heads": _obj(
        ["_id", "published_revision", "updated_at"],
        {"_id": _STR, "published_revision": _INT1, "updated_at": _DATE, "version": {"bsonType": "int"}},
    ),
    "legacy_mappings": _obj(
        ["_id", "source", "entity_type", "legacy_id", "new_item_id"],
        {"_id": _STR, "source": _STR, "entity_type": _STR, "legacy_id": _STR,
         "new_item_id": _STR, "source_checksum": _STR_NULL, "migration_version": _STR_NULL,
         "status": _STR_NULL, "created_at": _DATE_NULL},
    ),
    "enrollments": _obj(
        ["_id", "user_id", "curriculum_key", "dialect_id", "release_id", "status", "created_at"],
        {"_id": _STR, "user_id": _STR, "curriculum_key": _STR, "dialect_id": _STR,
         "release_id": _STR, "status": {"enum": ["active", "completed", "paused"]},
         "current_node_id": _STR_NULL, "projection": {"bsonType": "object"},
         "created_at": _DATE, "updated_at": _DATE, "version": {"bsonType": "int"}},
    ),
    "attempts": _obj(
        ["_id", "user_id", "dialect_id", "mode", "state", "started_at"],
        {"_id": _STR, "user_id": _STR, "dialect_id": _STR,
         "mode": {"enum": ["path", "practice", "review", "placement"]},
         "enrollment_id": _STR_NULL, "node_id": _STR_NULL,
         "content_ref": {"bsonType": ["object", "null"]}, "grading_config_ref": {"bsonType": ["object", "null"]},
         "selected_exercises": {"bsonType": "array"}, "seed": {"bsonType": ["int", "string", "null"]},
         "answers": {"bsonType": "array"}, "acknowledged_steps": {"bsonType": "array"},
         "state": {"enum": ["in_progress", "submitted"]},
         "score_correct": {"bsonType": ["int", "null"]}, "score_total": {"bsonType": ["int", "null"]},
         "passed": {"bsonType": ["bool", "null"]}, "started_at": _DATE, "submitted_at": _DATE_NULL,
         "version": {"bsonType": "int"}},
    ),
    "node_progress": _obj(
        ["_id", "enrollment_id", "node_id", "state"],
        {"_id": _STR, "enrollment_id": _STR, "node_id": _STR,
         "state": {"enum": ["coming_soon", "locked", "available", "in_progress", "completed"]},
         "first_passed_attempt_id": _STR_NULL, "latest_attempt_id": _STR_NULL,
         "completed_at": _DATE_NULL, "review_due": _BOOL, "version": {"bsonType": "int"}},
    ),
    "objective_progress": _obj(
        ["_id", "user_id", "dialect_id", "objective_id"],
        {"_id": _STR, "user_id": _STR, "dialect_id": _STR, "objective_id": _STR,
         "practice_count": {"bsonType": "int"}, "distinct_success_days": {"bsonType": "array"},
         "review_stage": {"bsonType": "int"}, "last_result": _STR_NULL,
         "last_success_day": _STR_NULL, "due_at": _DATE_NULL, "updated_at": _DATE,
         "version": {"bsonType": "int"}},
    ),
    "reward_ledger": _obj(
        ["_id", "user_id", "dialect_id", "source_key", "kind", "amount_xp", "created_at"],
        {"_id": _STR, "user_id": _STR, "enrollment_id": _STR_NULL, "dialect_id": _STR,
         "source_key": _STR, "kind": _STR, "amount_xp": {"bsonType": "int"},
         "rule_ref": {"bsonType": ["object", "null"]}, "event_day": _STR_NULL, "created_at": _DATE},
    ),
    "activity_days": _obj(
        ["_id", "user_id", "local_date", "created_at"],
        {"_id": _STR, "user_id": _STR, "local_date": _STR, "timezone_at_award": _STR,
         "qualifying_attempt_ids": {"bsonType": "array"}, "xp_total": {"bsonType": "int"},
         "created_at": _DATE},
    ),
    "bookmarks": _obj(
        ["_id", "user_id", "target_type", "target_id", "created_at"],
        {"_id": _STR, "user_id": _STR, "target_type": _STR, "target_id": _STR,
         "dialect_id": _STR_NULL, "created_at": _DATE},
    ),
    "idempotency_receipts": _obj(
        ["_id", "user_id", "scope", "key", "request_hash", "expires_at"],
        {"_id": _STR, "user_id": _STR, "scope": _STR, "key": _STR, "request_hash": _STR,
         "response_status": {"bsonType": "int"}, "response": {"bsonType": ["object", "null"]},
         "resource_ref": {"bsonType": ["object", "null"]}, "created_at": _DATE, "expires_at": _DATE},
    ),
    "media_assets": _obj(
        ["_id", "type", "status", "created_at"],
        {"_id": _STR, "type": {"enum": ["audio"]},
         "status": {"enum": ["queued", "generating", "ready", "failed", "quarantined"]},
         "audio_key": _STR_NULL, "utterance_id": _STR_NULL, "fingerprint": {"bsonType": ["object", "null"]},
         "gridfs_file_id": {"bsonType": ["objectId", "null"]}, "content_checksum": _STR_NULL,
         "mime": _STR_NULL, "bytes": {"bsonType": ["long", "int", "null"]},
         "duration_ms": {"bsonType": ["int", "null"]}, "route_ref": {"bsonType": ["object", "null"]},
         "voice_profile_ref": {"bsonType": ["object", "null"]}, "visibility": _STR,
         "human_reviewed": _BOOL, "ai_generated": _BOOL, "qa": {"bsonType": ["object", "null"]},
         "failure_category": _STR_NULL, "created_at": _DATE, "updated_at": _DATE_NULL,
         "version": {"bsonType": "int"}},
    ),
    "jobs": _obj(
        ["_id", "dedupe_key", "kind", "status", "available_at", "created_at"],
        {"_id": _STR, "dedupe_key": _STR, "kind": _STR,
         "status": {"enum": ["queued", "leased", "succeeded", "failed", "canceled"]},
         "payload": {"bsonType": "object"}, "available_at": _DATE, "lease_until": _DATE_NULL,
         "lease_token": _STR_NULL, "worker_id": _STR_NULL, "attempts": {"bsonType": "int"},
         "cancel_requested": _BOOL, "result_ref": {"bsonType": ["object", "null"]},
         "last_error": _STR_NULL, "next_retry_at": _DATE_NULL, "created_at": _DATE,
         "expires_at": _DATE_NULL, "version": {"bsonType": "int"}},
    ),
    "ai_runs": _obj(
        ["_id", "purpose", "created_at"],
        {"_id": _STR, "job_id": _STR_NULL, "purpose": _STR, "route_snapshot": {"bsonType": ["object", "null"]},
         "prompt_ref": {"bsonType": ["object", "null"]}, "input_ref": {"bsonType": ["object", "null"]},
         "output_ref": {"bsonType": ["object", "null"]}, "tokens": {"bsonType": ["int", "null"]},
         "characters": {"bsonType": ["int", "null"]}, "estimated_cost": {"bsonType": ["int", "null"]},
         "actual_cost": {"bsonType": ["int", "null"]}, "provider_request_id": _STR_NULL,
         "state": _STR_NULL, "created_at": _DATE},
    ),
    "budget_buckets": _obj(
        ["_id", "bucket_key", "period_start", "limit_microunits", "currency"],
        {"_id": _STR, "bucket_key": _STR, "period_start": _STR,
         "limit_microunits": {"bsonType": ["long", "int"]},
         "reserved_microunits": {"bsonType": ["long", "int"]},
         "spent_microunits": {"bsonType": ["long", "int"]},
         "currency": _STR, "version": {"bsonType": "int"}},
    ),
    "budget_reservations": _obj(
        ["_id", "request_key", "bucket_key", "period_start", "estimated_microunits", "state", "created_at"],
        {"_id": _STR, "request_key": _STR, "bucket_key": _STR, "period_start": _STR,
         "estimated_microunits": {"bsonType": ["long", "int"]},
         "actual_microunits": {"bsonType": ["long", "int", "null"]},
         "state": {"enum": ["reserved", "settled", "released"]}, "job_id": _STR_NULL,
         "created_at": _DATE, "settled_at": _DATE_NULL},
    ),
    "creators": _obj(
        ["_id", "slug", "name", "status", "created_at"],
        {"_id": _STR, "slug": _STR, "name": _STR, "bio": _STR_NULL,
         "profile_links": {"bsonType": "array"}, "dialect_ids": {"bsonType": "array"},
         "topic_ids": {"bsonType": "array"}, "attribution": {"bsonType": ["object", "null"]},
         "verification": {"bsonType": ["object", "null"]}, "image_media_id": _STR_NULL,
         "status": {"enum": ["draft", "published", "hidden", "archived"]},
         "featured_order": {"bsonType": ["int", "null"]}, "feature_window": {"bsonType": ["object", "null"]},
         "created_at": _DATE, "updated_at": _DATE_NULL, "version": {"bsonType": "int"}},
    ),
    "creator_resources": _obj(
        ["_id", "creator_id", "platform", "canonical_url", "status", "created_at"],
        {"_id": _STR, "creator_id": _STR,
         "platform": {"enum": ["instagram", "tiktok", "facebook", "youtube"]},
         "canonical_url": _STR, "provider_resource_id": _STR_NULL, "title": _STR_NULL,
         "description": _STR_NULL, "dialect_ids": {"bsonType": "array"},
         "topic_ids": {"bsonType": "array"}, "permitted_thumbnail_ref": {"bsonType": ["object", "null"]},
         "embed_state": _STR_NULL, "verification_at": _DATE_NULL,
         "status": {"enum": ["draft", "published", "hidden", "archived"]}, "created_at": _DATE},
    ),
    "reports": _obj(
        ["_id", "kind", "status", "created_at"],
        {"_id": _STR, "kind": {"enum": ["content", "audio", "creator_suggestion", "removal", "feedback"]},
         "reporter_user_id": _STR_NULL, "target_type": _STR_NULL, "target_id": _STR_NULL,
         "text": _STR_NULL, "source_url": _STR_NULL,
         "status": {"enum": ["open", "reviewing", "resolved", "dismissed"]},
         "resolution": _STR_NULL, "created_at": _DATE},
    ),
    "migration_runs": _obj(
        ["_id", "migration_key", "state", "created_at"],
        {"_id": _STR, "migration_key": _STR, "checksum": _STR_NULL, "state": _STR,
         "source_counts": {"bsonType": ["object", "null"]}, "mapped_counts": {"bsonType": ["object", "null"]},
         "rejected_ref": {"bsonType": ["object", "null"]}, "started_at": _DATE_NULL,
         "completed_at": _DATE_NULL, "created_at": _DATE},
    ),
}
