"""Audio acceptance tests (AUDIO-01, 02, 03, 06, login gating)."""
import asyncio

from app.jobs.worker import process_one
from tests.conftest import login


async def _first_turn(client):
    r = await client.get("/api/v1/dialogues/buying-bread-coffee-1")
    d = r.json()["data"]
    return d["id"], d["revision"], d["turns"][0]["id"]


async def _drain_worker():
    for _ in range(10):
        if not await process_one("test-worker"):
            break


async def test_visitor_cannot_generate_audio(client):
    item_id, revision, turn_id = await _first_turn(client)
    r = await client.post("/api/v1/audio/requests",
                          json={"content_ref": {"item_id": item_id, "revision": revision},
                                "turn_id": turn_id, "language_tag": "gsw-CH"})
    assert r.status_code == 403  # login required for first generation


async def test_lazy_generation_and_streaming(client, db):
    _, headers = await login(client, "audio@example.com")
    item_id, revision, turn_id = await _first_turn(client)
    r = await client.post("/api/v1/audio/requests",
                          json={"content_ref": {"item_id": item_id, "revision": revision},
                                "turn_id": turn_id, "language_tag": "gsw-CH"}, headers=headers)
    assert r.status_code in (200, 202)
    data = r.json()["data"]
    if data["status"] != "ready":
        await _drain_worker()
        rid = data["request_id"]
        data = (await client.get(f"/api/v1/audio/requests/{rid}")).json()["data"]
    assert data["status"] == "ready"
    assert data["ai_generated"] is True
    assert data["human_reviewed"] is False  # honest labelling

    stream_url = data["stream_url"]
    # HEAD
    h = await client.head(stream_url)
    assert h.status_code == 200
    size = int(h.headers["content-length"])
    assert size > 0
    assert h.headers["accept-ranges"] == "bytes"

    # Range request
    g = await client.get(stream_url, headers={"Range": "bytes=0-99"})
    assert g.status_code == 206
    assert g.headers["content-range"].startswith("bytes 0-99/")
    assert len(g.content) == 100


async def test_ready_asset_is_reused(client, db):
    _, headers = await login(client, "audioreuse@example.com")
    item_id, revision, turn_id = await _first_turn(client)
    body = {"content_ref": {"item_id": item_id, "revision": revision},
            "turn_id": turn_id, "language_tag": "gsw-CH"}
    await client.post("/api/v1/audio/requests", json=body, headers=headers)
    await _drain_worker()
    # Second request returns ready immediately, same media id.
    r = await client.post("/api/v1/audio/requests", json=body, headers=headers)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "ready"

    # Exactly one media asset for this audio key.
    media_id = r.json()["data"]["media_id"]
    asset = await db["media_assets"].find_one({"_id": media_id})
    count = await db["media_assets"].count_documents({"audio_key": asset["audio_key"]})
    assert count == 1


async def test_concurrent_requests_single_asset(client, db):
    _, headers = await login(client, "audioconc@example.com")
    # Use a different turn to avoid reuse from other tests.
    r = await client.get("/api/v1/dialogues/buying-bread-coffee-1")
    d = r.json()["data"]
    turn_id = d["turns"][2]["id"]
    body = {"content_ref": {"item_id": d["id"], "revision": d["revision"]},
            "turn_id": turn_id, "language_tag": "gsw-CH"}
    results = await asyncio.gather(
        client.post("/api/v1/audio/requests", json=body, headers=headers),
        client.post("/api/v1/audio/requests", json=body, headers=headers),
        client.post("/api/v1/audio/requests", json=body, headers=headers),
    )
    assert all(rr.status_code in (200, 202) for rr in results)
    await _drain_worker()
    # Determine the audio key via the utterance and assert a single asset + job.
    rev = await db["content_revisions"].find_one({"item_id": d["id"], "revision": d["revision"]})
    turn = next(t for t in rev["payload"]["turns"] if t["id"] == turn_id)
    assets = await db["media_assets"].count_documents({"utterance_id": turn["utterance_id"]})
    assert assets == 1
