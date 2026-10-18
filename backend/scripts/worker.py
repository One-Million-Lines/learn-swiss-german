"""Standalone durable job worker process.

Usage::

    python -m scripts.worker
"""
from __future__ import annotations

import asyncio
import sys

sys.path.insert(0, ".")

from app.config import get_settings  # noqa: E402
from app.db import client as db_client  # noqa: E402
from app.jobs.worker import run_worker  # noqa: E402


async def _main() -> None:
    await db_client.connect(get_settings())
    try:
        await run_worker("standalone")
    finally:
        await db_client.disconnect()


if __name__ == "__main__":
    asyncio.run(_main())
