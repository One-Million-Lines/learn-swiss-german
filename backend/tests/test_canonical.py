"""Canonicalization + audio fingerprint determinism (spec 02 §5, AUDIO-02)."""
from app.content.canonical import (
    audio_fingerprint,
    audio_key,
    canonicalize,
    text_sha256,
)


def _fp(**overrides):
    base = dict(
        text_sha256_value="a" * 64, language_tag="gsw-CH", dialect_id="gsw-zh",
        pronunciation_context_id="default", spoken_text_sha256="a" * 64,
        provider="fake", model="fake-tts-1", model_revision="fake-rev-1",
        voice_id="dev-fake", voice_profile_version=1, synthesis_version=1,
        pronunciation_lexicon_version=1, fmt="wav", sample_rate_hz=24000,
    )
    base.update(overrides)
    return audio_fingerprint(**base)


def test_canonicalization_preserves_umlauts_and_collapses_whitespace():
    assert canonicalize("  Grüezi\r\n  wohl   welt  ") == "Grüezi\nwohl welt"
    # Case and umlauts are meaning-bearing and preserved.
    assert canonicalize("Chäs") == "Chäs"


def test_audio_key_is_pinned_and_stable():
    # Exact serialization fixture (spec requires a pinned hash).
    assert audio_key(_fp()) == "6ccd600fbc34d80573bc46451b8fc1633d74301907b1354ae73a59887d4dc674"


def test_changing_dialect_voice_model_changes_key():
    base = audio_key(_fp())
    assert audio_key(_fp(dialect_id="gsw-be")) != base
    assert audio_key(_fp(voice_id="other")) != base
    assert audio_key(_fp(model="other-model")) != base
    assert audio_key(_fp(synthesis_version=2)) != base


def test_same_inputs_same_key():
    assert audio_key(_fp()) == audio_key(_fp())


def test_text_hash_matches_canonical():
    assert text_sha256(canonicalize("Grüezi")) == text_sha256("Grüezi")
