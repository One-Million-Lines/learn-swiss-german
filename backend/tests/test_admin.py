"""Admin RBAC + publishing acceptance tests (ADMIN-01, ADMIN-02)."""
from tests.conftest import login


async def _set_roles(db, email, roles):
    await db["users"].update_one({"email_normalized": email}, {"$set": {"roles": roles}})


async def test_learner_cannot_reach_admin(client):
    _, headers = await login(client, "plainlearner@example.com")
    r = await client.get("/api/v1/admin/content", headers=headers)
    assert r.status_code == 403


async def test_editor_can_draft_but_not_publish(client, db):
    _, headers = await login(client, "editor1@example.com")
    await _set_roles(db, "editor1@example.com", ["editor"])

    r = await client.post("/api/v1/admin/content", headers=headers, json={
        "kind": "pattern", "slug": "test-pattern-x", "title": "Test pattern",
        "payload": {"title": "Test pattern", "description": "d", "examples": []},
    })
    assert r.status_code == 200
    item_id = r.json()["data"]["_id"]

    assert (await client.post(f"/api/v1/admin/content/{item_id}/submit-review", headers=headers)).status_code == 200
    # Editor lacks publisher capability.
    assert (await client.post(f"/api/v1/admin/content/{item_id}/approve", headers=headers)).status_code == 403
    assert (await client.post(f"/api/v1/admin/content/{item_id}/publish", headers=headers)).status_code in (403, 409)


async def test_publisher_can_publish(client, db):
    _, headers = await login(client, "pub1@example.com")
    await _set_roles(db, "pub1@example.com", ["editor", "publisher"])

    r = await client.post("/api/v1/admin/content", headers=headers, json={
        "kind": "pattern", "slug": "test-pattern-y", "title": "Publishable",
        "payload": {"title": "Publishable", "description": "d", "examples": []},
    })
    item_id = r.json()["data"]["_id"]
    await client.post(f"/api/v1/admin/content/{item_id}/submit-review", headers=headers)
    await client.post(f"/api/v1/admin/content/{item_id}/approve", headers=headers)
    pub = await client.post(f"/api/v1/admin/content/{item_id}/publish", headers=headers)
    assert pub.status_code == 200
    item = await db["content_items"].find_one({"_id": item_id})
    assert item["status"] == "published" and item["published_revision"] == 1
    # Audit recorded.
    audit = await db["audit_log"].find_one({"action": "content.publish", "target_id": item_id})
    assert audit is not None


async def test_role_change_is_audited(client, db):
    _, headers = await login(client, "admin1@example.com")
    await _set_roles(db, "admin1@example.com", ["administrator"])
    # Create the target user directly (avoid clobbering the admin session cookie).
    from app.common.ids import new_id
    from app.common.timeutil import utcnow
    target_id = new_id()
    await db["users"].insert_one({
        "_id": target_id, "schema_version": 1, "email_normalized": "target1@example.com",
        "email_verified_at": utcnow(), "display_name": None, "roles": [], "status": "active",
        "onboarding": {}, "preferences": {}, "created_at": utcnow(), "updated_at": utcnow(), "version": 1,
    })

    r = await client.post(f"/api/v1/admin/users/{target_id}/roles", headers=headers,
                          json={"roles": ["editor"]})
    assert r.status_code == 200
    fresh = await db["users"].find_one({"_id": target_id})
    assert fresh["roles"] == ["editor"]
    audit = await db["audit_log"].find_one({"action": "user.set_roles", "target_id": target_id})
    assert audit is not None
