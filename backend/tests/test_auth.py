"""Authentication acceptance tests (AUTH-01..05)."""
import pytest

from tests.conftest import login
from app.auth.email_adapter import SENT_MESSAGES


async def test_generic_response_for_any_email(client):
    r1 = await client.post("/api/v1/auth/magic-links",
                           json={"email": "exists@example.com", "return_path": "/auth/callback"})
    r2 = await client.post("/api/v1/auth/magic-links",
                           json={"email": "unknown-person@example.com", "return_path": "/auth/callback"})
    assert r1.status_code == 202 and r2.status_code == 202
    assert r1.json()["data"]["status"] == r2.json()["data"]["status"]


async def test_invalid_return_path_rejected(client):
    r = await client.post("/api/v1/auth/magic-links",
                          json={"email": "a@example.com", "return_path": "https://evil.example/callback"})
    assert r.status_code == 400


async def test_token_is_single_use(client):
    SENT_MESSAGES.clear()
    await client.post("/api/v1/auth/magic-links",
                      json={"email": "single@example.com", "return_path": "/auth/callback"})
    token = SENT_MESSAGES[-1]["link"].split("#token=")[1]
    r1 = await client.post("/api/v1/auth/magic-links/consume", json={"token": token})
    assert r1.status_code == 200
    r2 = await client.post("/api/v1/auth/magic-links/consume", json={"token": token})
    assert r2.status_code == 409


async def test_refresh_rotation_and_replay_revokes_family(client):
    await login(client, "refresh@example.com")
    original_refresh = client.cookies.get("ss_refresh")
    assert original_refresh

    r = await client.post("/api/v1/auth/refresh")
    assert r.status_code == 200
    new_refresh = client.cookies.get("ss_refresh")
    assert new_refresh != original_refresh

    # Replay the original refresh -> family revoked.
    r = await client.post("/api/v1/auth/refresh", cookies={"ss_refresh": original_refresh})
    assert r.status_code == 400
    # After revocation the rotated refresh is also unusable.
    r = await client.post("/api/v1/auth/refresh", cookies={"ss_refresh": new_refresh})
    assert r.status_code == 400


async def test_csrf_required_for_cookie_writes(client):
    await login(client, "csrf@example.com")
    # No CSRF header -> rejected.
    r = await client.post("/api/v1/me/bookmarks",
                          json={"target_type": "dialogue", "target_id": "x"})
    assert r.status_code == 403


async def test_learner_cannot_access_admin(client):
    _, headers = await login(client, "nonadmin@example.com")
    r = await client.get("/api/v1/admin/users", headers=headers)
    assert r.status_code == 403


async def test_logout_revokes_session(client):
    _, headers = await login(client, "logout@example.com")
    assert (await client.get("/api/v1/me")).status_code == 200
    await client.post("/api/v1/auth/logout", headers=headers)
    # Access token still in cookie but session is revoked.
    r = await client.get("/api/v1/me")
    assert r.status_code == 401
