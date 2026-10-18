"""Deterministic in-process providers for local dev and tests.

The speech provider emits a valid WAV so the media pipeline (validate, store,
stream) can be exercised without any external cost or a human-reviewed voice.
It is explicitly NOT a real Swiss-dialect voice.
"""
from __future__ import annotations

import hashlib
import math
import struct
from typing import Any, Dict


def _sine_wav(seed_bytes: bytes, *, sample_rate: int, duration_ms: int) -> bytes:
    """Build a mono 16-bit PCM WAV deterministically from a seed."""
    num_samples = max(1, int(sample_rate * duration_ms / 1000))
    freq = 180 + (seed_bytes[0] if seed_bytes else 0) % 220  # 180–400 Hz
    frames = bytearray()
    for n in range(num_samples):
        sample = int(12000 * math.sin(2 * math.pi * freq * (n / sample_rate)))
        frames += struct.pack("<h", sample)

    data_size = len(frames)
    byte_rate = sample_rate * 2
    header = b"RIFF" + struct.pack("<I", 36 + data_size) + b"WAVE"
    header += b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, byte_rate, 2, 16)
    header += b"data" + struct.pack("<I", data_size)
    return bytes(header) + bytes(frames)


class FakeSpeechProvider:
    name = "fake"

    def synthesize(self, *, text: str, voice_profile: Dict[str, Any]) -> Dict[str, Any]:
        sample_rate = int(voice_profile.get("sample_rate_hz", 24000))
        # ~60ms per character, capped at the per-asset limit.
        duration_ms = min(60_000, max(400, len(text) * 60))
        seed = hashlib.sha256((voice_profile.get("voice_id", "") + text).encode("utf-8")).digest()
        audio = _sine_wav(seed, sample_rate=sample_rate, duration_ms=duration_ms)
        return {
            "bytes": audio,
            "mime": "audio/wav",
            "format": "wav",
            "duration_ms": duration_ms,
            "sample_rate_hz": sample_rate,
            "provider_request_id": "fake-" + seed.hex()[:16],
            "cost_microunits": 100,
        }


def validate_audio(result: Dict[str, Any]) -> None:
    """Reject malformed/empty provider output before it can become 'ready'."""
    data = result.get("bytes") or b""
    if len(data) < 64:
        raise ValueError("audio too small")
    if result.get("duration_ms", 0) <= 0:
        raise ValueError("zero duration")
    if result.get("format") == "wav":
        if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
            raise ValueError("invalid WAV container")
