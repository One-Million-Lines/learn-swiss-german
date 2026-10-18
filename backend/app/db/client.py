"""Async MongoDB client lifecycle (PyMongo AsyncMongoClient, no Motor)."""
from __future__ import annotations

from typing import Optional

from gridfs import AsyncGridFSBucket
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.config import Settings, get_settings
from app.common import tracing

_client: Optional[AsyncMongoClient] = None
_db: Optional[AsyncDatabase] = None
_settings: Optional[Settings] = None


async def connect(settings: Optional[Settings] = None) -> AsyncDatabase:
    """Create the shared async client and verify connectivity."""
    global _client, _db, _settings
    _settings = settings or get_settings()
    _client = AsyncMongoClient(
        _settings.mongodb_uri,
        uuidRepresentation="standard",
        tz_aware=True,
        serverSelectionTimeoutMS=5000,
    )
    await _client.admin.command("ping")
    _db = _client[_settings.mongodb_database]
    tracing.info("mongo_connected", database=_settings.mongodb_database)
    return _db


async def disconnect() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
        tracing.info("mongo_disconnected")


def get_db() -> AsyncDatabase:
    if _db is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return _db


def get_client() -> AsyncMongoClient:
    if _client is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return _client


def gridfs_bucket(bucket: str = "media") -> AsyncGridFSBucket:
    return AsyncGridFSBucket(get_db(), bucket_name=bucket)
