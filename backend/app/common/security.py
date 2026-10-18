"""Cryptographic helpers built on the Python standard library.

We intentionally avoid third-party crypto packages: magic-link tokens, session
credentials and CSRF tokens are opaque random values; only their SHA-256 hashes
are stored. Comparisons use constant-time equality.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets


def random_token(num_bytes: int = 32) -> str:
    """URL-safe random token with at least ``num_bytes`` of entropy."""
    return secrets.token_urlsafe(num_bytes)


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)


def normalize_email(email: str) -> str:
    """Lower-case + trim only.

    Per spec we must NOT apply Gmail dot/plus rewrites; the local part is
    preserved apart from surrounding whitespace and case folding of the domain.
    """
    email = (email or "").strip()
    if "@" not in email:
        return email.lower()
    local, _, domain = email.rpartition("@")
    return f"{local}@{domain.lower()}"


def mask_email(email: str) -> str:
    local, _, domain = (email or "").partition("@")
    if not domain:
        return "•••"
    shown = local[:1]
    return f"{shown}{'•' * max(2, len(local) - 1)}@{domain}"
