"""Transaction helper using the driver's retry-aware with_transaction."""
from __future__ import annotations

from typing import Awaitable, Callable, TypeVar

from app.db.client import get_client

T = TypeVar("T")


async def in_transaction(callback: Callable[[object], Awaitable[T]]) -> T:
    """Run ``callback(session)`` inside a transaction.

    Uses the driver's ``with_transaction``, which automatically retries on
    TransientTransactionError and UnknownTransactionCommitResult (spec: "retry
    the entire transaction on transient conflicts").
    """
    client = get_client()
    async with client.start_session() as session:
        return await session.with_transaction(lambda s: callback(s))
