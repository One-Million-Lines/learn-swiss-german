"""Text canonicalization (v1) and utterance/audio hashing.

Canonicalization version 1 (spec 02 §5): Unicode NFC, CRLF/CR to LF, trim
leading/trailing whitespace, collapse repeated horizontal whitespace. Case,
punctuation, apostrophes and umlauts are preserved — they are meaning-bearing.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Dict

CANONICALIZATION_VERSION = 1

_HORIZONTAL_WS = re.compile(r"[ \t\f\v]+")


def canonicalize(text: str) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse runs of horizontal whitespace, preserve single newlines.
    lines = [_HORIZONTAL_WS.sub(" ", line).strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def text_sha256(canonical_text: str) -> str:
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


def utterance_fields(text: str) -> Dict[str, Any]:
    canonical = canonicalize(text)
    return {
        "text": text,
        "canonical_text": canonical,
        "text_sha256": text_sha256(canonical),
        "canonicalization_version": CANONICALIZATION_VERSION,
    }


# --------------------------------------------------------------------------- #
# Audio fingerprint (spec 02 §5)                                               #
# --------------------------------------------------------------------------- #
def audio_fingerprint(
    *,
    text_sha256_value: str,
    language_tag: str,
    dialect_id: str | None,
    pronunciation_context_id: str,
    spoken_text_sha256: str,
    provider: str,
    model: str,
    model_revision: str,
    voice_id: str,
    voice_profile_version: int,
    synthesis_version: int,
    pronunciation_lexicon_version: int,
    style: str = "conversational-neutral",
    speed: str = "1.00",
    fmt: str = "mp3",
    sample_rate_hz: int = 24000,
    generation_variant: int = 0,
    provider_options: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Build the canonical fingerprint document (explicit nulls, normalized types)."""
    return {
        "key_schema": 1,
        "text_sha256": text_sha256_value,
        "language_tag": language_tag,
        "dialect_id": dialect_id,
        "pronunciation_context_id": pronunciation_context_id,
        "spoken_text_sha256": spoken_text_sha256,
        "provider": provider,
        "model": model,
        "model_revision": model_revision,
        "voice_id": voice_id,
        "voice_profile_version": int(voice_profile_version),
        "synthesis_version": int(synthesis_version),
        "pronunciation_lexicon_version": int(pronunciation_lexicon_version),
        "style": style,
        "speed": speed,
        "format": fmt,
        "sample_rate_hz": int(sample_rate_hz),
        "generation_variant": int(generation_variant),
        "provider_options": provider_options or {},
    }


def audio_key(fingerprint: Dict[str, Any]) -> str:
    """Deterministic audio_key = sha256(canonical fingerprint JSON).

    Sorted keys, UTF-8, compact separators, explicit nulls.
    """
    canonical_json = json.dumps(
        fingerprint, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
