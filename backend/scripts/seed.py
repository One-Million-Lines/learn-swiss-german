"""Seed non-content baseline: dialects and versioned app configuration.

Idempotent. Speech routes stay disabled until a voice profile passes evaluation.
"""
from __future__ import annotations

import sys

from pymongo import MongoClient

sys.path.insert(0, ".")

from app.common.ids import deterministic_id  # noqa: E402
from app.common.timeutil import utcnow  # noqa: E402
from app.config import get_settings  # noqa: E402

DIALECTS = [
    {
        "code": "gsw-zh",
        "labels": {"en": "Zürichdeutsch", "de": "Zürichdeutsch"},
        "description": {"en": "Swiss German as spoken around Zürich."},
        "regional_variety": "Zürich city variety",
        "language_tag": "gsw-CH",
        "status": "enabled",
        "voice_review_status": "pending",
        "sort_order": 0,
    },
    {
        "code": "gsw-be",
        "labels": {"en": "Berndeutsch", "de": "Berndeutsch"},
        "description": {"en": "Swiss German as spoken around Bern."},
        "regional_variety": "Bern city variety",
        "language_tag": "gsw-CH",
        "status": "enabled",
        "voice_review_status": "pending",
        "sort_order": 1,
    },
    {
        "code": "gsw-vs",
        "labels": {"en": "Walliserdeutsch"},
        "description": {"en": "Valais Swiss German (planned)."},
        "regional_variety": "Valais varieties",
        "language_tag": "gsw-CH",
        "status": "coming_soon",
        "voice_review_status": "pending",
        "sort_order": 2,
    },
    {
        "code": "gsw-sg",
        "labels": {"en": "St. Gallerdeutsch"},
        "description": {"en": "St. Gallen Swiss German (planned)."},
        "regional_variety": "St. Gallen varieties",
        "language_tag": "gsw-CH",
        "status": "coming_soon",
        "voice_review_status": "pending",
        "sort_order": 3,
    },
]

CONFIG = {
    "homepage": {
        "hero": {
            "title": "Grüezi! Understand Swiss German in real life.",
            "subtitle": "You already know some German. Learn how everyday conversations actually sound in Switzerland.",
            "primary_cta": "Start discovering",
            "secondary_cta": "Explore dialogues",
            "reassurance": "Free to learn",
        },
        "sections": ["hero", "sample", "journey", "daily", "topics", "creators", "how_it_works"],
    },
    "grading": {
        "version": "grading-v1",
        "pass_threshold_numerator": 80,
        "pass_threshold_denominator": 100,
        "min_items": 5,
        "checkpoint_min_items": 10,
        "missing_answer_policy": "incorrect",
        "normalization": {"unicode": "NFC", "case": "exercise", "collapse_whitespace": True},
    },
    "rewards": {
        "version": "rewards-v1",
        "lesson_first_completion_xp": 20,
        "checkpoint_first_pass_xp": 50,
        "review_session_xp": 5,
        "review_daily_cap_xp": 20,
        "review_min_items": 5,
        "review_min_accuracy": 80,
        "intervals_days": [1, 3, 7, 14, 30],
    },
    "budgets": {
        "version": "budgets-v1",
        "audio_uncached_per_user_per_day": 30,
        "audio_new_requests_per_user_per_minute": 5,
        "text_max_chars_per_turn": 600,
        "speech_max_seconds_per_asset": 60,
        "currency": "USD",
    },
    "ai_routes": {
        "version": "ai-routes-v1",
        "routes": {
            "lesson.author": {"capability": "text", "provider": "fake", "model": "fake-author-1", "status": "enabled"},
            "lesson.qa": {"capability": "text", "provider": "fake", "model": "fake-qa-1", "status": "enabled"},
            "translation.en": {"capability": "text", "provider": "fake", "model": "fake-translate-1", "status": "enabled"},
            "translation.es": {"capability": "text", "provider": "fake", "model": "fake-translate-1", "status": "enabled"},
            "speech.gsw_zh": {"capability": "speech", "provider": "fake", "model": "fake-tts-1", "voice_id": "zh-default", "status": "disabled"},
            "speech.gsw_be": {"capability": "speech", "provider": "fake", "model": "fake-tts-1", "voice_id": "be-default", "status": "disabled"},
        },
    },
    "voice_profiles": {
        "version": "voice-profiles-v1",
        "profiles": {
            # Dev/test profile for the fake provider so lazy audio can be exercised
            # end-to-end without a real, human-reviewed voice.
            "voice.dev_fake": {
                "dialect_id": "gsw-zh", "provider": "fake", "model": "fake-tts-1",
                "model_revision": "fake-rev-1", "voice_id": "dev-fake",
                "voice_profile_version": 1, "synthesis_version": 1,
                "pronunciation_lexicon_version": 1, "sample_rate_hz": 24000,
                "format": "mp3", "status": "enabled_dev", "human_reviewed": False,
            }
        },
    },
}


def main() -> int:
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, uuidRepresentation="standard", tz_aware=True)
    db = client[settings.mongodb_database]
    now = utcnow()

    for d in DIALECTS:
        db["dialects"].replace_one(
            {"code": d["code"]},
            {**d, "_id": deterministic_id("dialect", d["code"]), "schema_version": 1,
             "created_at": now, "updated_at": now, "version": 1},
            upsert=True,
        )

    for key, payload in CONFIG.items():
        existing = db["app_config"].find_one({"key": key, "revision": 1})
        if existing is None:
            db["app_config"].insert_one({
                "_id": deterministic_id("app_config", key, "1"),
                "key": key, "revision": 1, "status": "published",
                "payload": payload, "created_by": "system", "created_at": now,
            })
        db["config_heads"].replace_one(
            {"_id": key},
            {"_id": key, "published_revision": 1, "updated_at": now, "version": 1},
            upsert=True,
        )

    print(f"Seeded {len(DIALECTS)} dialects and {len(CONFIG)} config keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
