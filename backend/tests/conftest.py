"""Shared test fixtures: ephemeral test database on the dev replica set.

Tests run against a real single-node MongoDB replica set (transactions required).
The test database is fully rebuilt once per session from the migration/seed/
curriculum pipeline, then dropped at the end.
"""
from __future__ import annotations

import os

import pytest
import pytest_asyncio

os.environ.setdefault("VT_ENV", "test")
os.environ["MONGODB_DATABASE"] = "swissspeak_test"
os.environ["RUN_INPROCESS_WORKER"] = "0"
os.environ.setdefault("MONGODB_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0")

from pymongo import MongoClient  # noqa: E402

from app.config import get_settings  # noqa: E402

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data-json"))


@pytest.fixture(scope="session", autouse=True)
def _build_database():
    """Drop + rebuild the test database once per session."""
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, uuidRepresentation="standard", tz_aware=True)
    client.drop_database(settings.mongodb_database)

    # 1. Collections, validators, indexes.
    from scripts.setup_database import main as setup_main
    import sys

    sys.argv = ["setup", "--apply", "--database", settings.mongodb_database]
    setup_main()

    db = client[settings.mongodb_database]
    # 2. Migration + seed + curriculum.
    from app.content.migrate import run_migration
    run_migration(db, DATA_DIR, apply=True)
    from scripts.seed import DIALECTS, CONFIG
    from app.common.ids import deterministic_id
    from app.common.timeutil import utcnow
    now = utcnow()
    for d in DIALECTS:
        db["dialects"].replace_one({"code": d["code"]},
            {**d, "_id": deterministic_id("dialect", d["code"]), "schema_version": 1,
             "created_at": now, "updated_at": now, "version": 1}, upsert=True)
    for key, payload in CONFIG.items():
        if db["app_config"].find_one({"key": key, "revision": 1}) is None:
            db["app_config"].insert_one({"_id": deterministic_id("app_config", key, "1"),
                "key": key, "revision": 1, "status": "published", "payload": payload,
                "created_by": "system", "created_at": now})
        db["config_heads"].replace_one({"_id": key},
            {"_id": key, "published_revision": 1, "updated_at": now, "version": 1}, upsert=True)
    from app.learning.curriculum_build import build
    build(db, "gsw-zh")

    yield
    client.drop_database(settings.mongodb_database)
    client.close()


@pytest_asyncio.fixture
async def db():
    from app.db import client as db_client
    database = await db_client.connect(get_settings())
    # Clear throttle buckets so shared-IP test traffic is not rate-limited.
    await database["rate_limit_buckets"].delete_many({})
    try:
        yield database
    finally:
        await db_client.disconnect()


@pytest_asyncio.fixture
async def client(db):
    """httpx AsyncClient bound to the ASGI app (DB connected via `db` fixture)."""
    import httpx
    from app.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def login(client, email: str):
    """Helper: perform a magic-link login and return (client, csrf, headers)."""
    from app.auth.email_adapter import SENT_MESSAGES

    SENT_MESSAGES.clear()
    r = await client.post("/api/v1/auth/magic-links",
                          json={"email": email, "return_path": "/auth/callback"})
    assert r.status_code == 202
    link = SENT_MESSAGES[-1]["link"]
    token = link.split("#token=")[1]
    r = await client.post("/api/v1/auth/magic-links/consume", json={"token": token})
    assert r.status_code == 200
    csrf = r.json()["data"]["csrf_token"]
    headers = {"X-CSRF-Token": csrf, "Origin": "http://localhost:5306"}
    return csrf, headers
