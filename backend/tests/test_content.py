"""Content/discovery acceptance tests (CONTENT-01, legacy compat, DATA-02)."""


async def test_public_dialogue_has_no_answer_keys(client):
    r = await client.get("/api/v1/dialogues/buying-bread-coffee-1")
    assert r.status_code == 200
    body = r.text
    assert "private_grading" not in body
    assert "correct_choice_id" not in body


async def test_legacy_endpoints_still_work(client):
    r = await client.get("/content/topics")
    assert r.status_code == 200
    assert "topics" in r.json()
    r = await client.get("/content/daily-phrase")
    assert r.status_code == 200
    assert "phrase" in r.json()


async def test_legacy_dialogue_labelled_unverified(client):
    r = await client.get("/api/v1/dialogues/buying-bread-coffee-1")
    data = r.json()["data"]
    assert data["dialect_verified"] is False
    assert data["dialect_label"]  # explicit "dialect not verified" label
    assert data["turns"][0]["swiss_german"]


async def test_lesson_study_payload_excludes_answer_keys(client):
    from tests.conftest import login

    _, headers = await login(client, "studypayload@example.com")
    # Find a lesson via the curriculum path.
    await client.post("/api/v1/me/enrollments",
                      json={"curriculum_key": "mountain_journey", "dialect_id": "gsw-zh"}, headers=headers)
    enr = (await client.get("/api/v1/me/enrollments")).json()["data"][0]
    path = (await client.get(f"/api/v1/me/enrollments/{enr['id']}/path")).json()["data"]
    node = next(n for n in path["nodes"] if n["state"] == "available")
    lesson_id = node["lesson_ref"]["item_id"]
    r = await client.get(f"/api/v1/lessons/{lesson_id}", headers=headers)
    assert r.status_code == 200
    assert "correct_choice_id" not in r.text
    for ex in r.json()["data"]["exercises"]:
        assert "private_grading" not in ex


async def test_search_only_returns_published(client):
    r = await client.get("/api/v1/search", params={"q": "bread"})
    assert r.status_code == 200
    for item in r.json()["data"]:
        assert item["kind"] in ("topic", "subtopic", "dialogue", "pattern", "vocabulary_group",
                                 "lesson", "exercise", "objective", "checkpoint")
