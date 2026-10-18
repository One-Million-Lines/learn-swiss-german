"""Stable ID helpers.

Application ``_id`` values are UUID strings. Imported legacy entities get a
*deterministic* UUIDv5 so re-running the migration never changes an ID.
"""
from __future__ import annotations

import uuid

# Project UUIDv5 namespace (fixed, do not change — it anchors deterministic IDs).
NAMESPACE = uuid.UUID("b7f1c2a0-9d4e-5c3b-8a21-000000000001")


def new_id() -> str:
    """Random UUID4 string for freshly created records."""
    return str(uuid.uuid4())


def deterministic_id(*parts: str) -> str:
    """Deterministic UUIDv5 derived from the given parts.

    Used by the migration so that a given legacy entity always maps to the same
    MongoDB ``_id`` across repeated imports.
    """
    name = "|".join(str(p) for p in parts)
    return str(uuid.uuid5(NAMESPACE, name))
