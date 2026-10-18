"""Time helpers.

All stored timestamps are timezone-aware UTC ``datetime`` objects (BSON dates).
Local-day calculations for streaks/reviews use the learner's stored IANA zone.
"""
from __future__ import annotations

from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def local_day(dt: datetime, tz_name: str) -> str:
    """Return the ``YYYY-MM-DD`` local date for an instant in a given zone."""
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("Europe/Zurich")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).date().isoformat()


def editorial_date(tz_name: str = "Europe/Zurich", at: datetime | None = None) -> str:
    """Deterministic editorial date used for daily selections."""
    return local_day(at or utcnow(), tz_name)
