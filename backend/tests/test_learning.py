"""Learning engine acceptance tests (LEARN-01, 02, 04, review mastery)."""
from tests.conftest import login


async def _correct_answers(db, exercise_ids):
    """Build correct answers by reading server-only private grading."""
    answers = []
    for ex_id in exercise_ids:
        item = await db["content_items"].find_one({"_id": ex_id})
        rev = await db["content_revisions"].find_one(
            {"item_id": ex_id, "revision": item["published_revision"]})
        answers.append({"exercise_id": ex_id,
                        "choice_id": rev["private_grading"]["correct_choice_id"]})
    return answers


async def _setup_attempt(client, db, headers):
    await client.post("/api/v1/me/enrollments",
                      json={"curriculum_key": "mountain_journey", "dialect_id": "gsw-zh"}, headers=headers)
    enr = (await client.get("/api/v1/me/enrollments")).json()["data"][0]
    path = (await client.get(f"/api/v1/me/enrollments/{enr['id']}/path")).json()["data"]
    node = next(n for n in path["nodes"] if n["state"] == "available")
    lesson_id = node["lesson_ref"]["item_id"]
    r = await client.post("/api/v1/attempts",
                          json={"mode": "path", "lesson_id": lesson_id,
                                "enrollment_id": enr["id"], "node_id": node["id"],
                                "dialect_id": "gsw-zh"}, headers=headers)
    attempt = r.json()["data"]
    return enr, node, lesson_id, attempt


async def test_pass_threshold_80_percent(client, db):
    _, headers = await login(client, "learn80@example.com")
    enr, node, lesson_id, attempt = await _setup_attempt(client, db, headers)
    ex_ids = [e["id"] for e in attempt["exercises"]]
    correct = await _correct_answers(db, ex_ids)

    # 4/5 correct -> pass. Make the 5th wrong.
    wrong_choice = "a" if correct[-1]["choice_id"] != "a" else "b"
    answers = correct[:-1] + [{"exercise_id": ex_ids[-1], "choice_id": wrong_choice}]
    r = await client.post(f"/api/v1/attempts/{attempt['id']}/submit",
                          json={"attempt_version": attempt["version"], "answers": answers,
                                "acknowledged_steps": ["scene"]},
                          headers={**headers, "Idempotency-Key": "k-80"})
    data = r.json()["data"]
    assert data["score"] == {"correct": 4, "total": 5}
    assert data["passed"] is True
    assert data["awarded_xp"] == 20


async def test_fail_below_threshold(client, db):
    _, headers = await login(client, "learnfail@example.com")
    enr, node, lesson_id, attempt = await _setup_attempt(client, db, headers)
    ex_ids = [e["id"] for e in attempt["exercises"]]
    correct = await _correct_answers(db, ex_ids)
    # 3/5 correct -> fail.
    bad = [{"exercise_id": ex_ids[i], "choice_id": ("a" if correct[i]["choice_id"] != "a" else "b")}
           for i in (3, 4)]
    answers = correct[:3] + bad
    r = await client.post(f"/api/v1/attempts/{attempt['id']}/submit",
                          json={"attempt_version": attempt["version"], "answers": answers,
                                "acknowledged_steps": []},
                          headers={**headers, "Idempotency-Key": "k-fail"})
    data = r.json()["data"]
    assert data["score"]["correct"] == 3
    assert data["passed"] is False
    assert data["awarded_xp"] == 0


async def test_client_supplied_score_is_ignored(client, db):
    _, headers = await login(client, "cheat@example.com")
    enr, node, lesson_id, attempt = await _setup_attempt(client, db, headers)
    ex_ids = [e["id"] for e in attempt["exercises"]]
    # Attempt to inject a fake score/passed/xp — server ignores extra fields.
    answers = [{"exercise_id": ex_ids[0], "choice_id": "a"}]
    r = await client.post(f"/api/v1/attempts/{attempt['id']}/submit",
                          json={"attempt_version": attempt["version"], "answers": answers,
                                "acknowledged_steps": [], "score": 999, "passed": True,
                                "awarded_xp": 9999},
                          headers={**headers, "Idempotency-Key": "k-cheat"})
    data = r.json()["data"]
    assert data["score"]["total"] == 5
    assert data["awarded_xp"] in (0, 20)


async def test_submit_idempotent_single_reward(client, db):
    _, headers = await login(client, "idem@example.com")
    enr, node, lesson_id, attempt = await _setup_attempt(client, db, headers)
    ex_ids = [e["id"] for e in attempt["exercises"]]
    answers = await _correct_answers(db, ex_ids)
    body = {"attempt_version": attempt["version"], "answers": answers, "acknowledged_steps": []}
    results = []
    for _ in range(5):
        r = await client.post(f"/api/v1/attempts/{attempt['id']}/submit", json=body,
                              headers={**headers, "Idempotency-Key": "once"})
        results.append(r.json()["data"])
    assert all(x["passed"] for x in results)
    # Exactly one reward ledger entry for this node.
    count = await db["reward_ledger"].count_documents(
        {"source_key": f"lesson:{enr['id']}:{node['id']}"})
    assert count == 1


async def test_same_key_different_body_conflict(client, db):
    _, headers = await login(client, "idemconf@example.com")
    enr, node, lesson_id, attempt = await _setup_attempt(client, db, headers)
    ex_ids = [e["id"] for e in attempt["exercises"]]
    answers = await _correct_answers(db, ex_ids)
    await client.post(f"/api/v1/attempts/{attempt['id']}/submit",
                      json={"attempt_version": attempt["version"], "answers": answers, "acknowledged_steps": []},
                      headers={**headers, "Idempotency-Key": "dup"})
    r = await client.post(f"/api/v1/attempts/{attempt['id']}/submit",
                          json={"attempt_version": attempt["version"], "answers": answers[:1], "acknowledged_steps": []},
                          headers={**headers, "Idempotency-Key": "dup"})
    assert r.status_code == 409


async def test_locked_node_cannot_be_attempted(client, db):
    _, headers = await login(client, "locked@example.com")
    await client.post("/api/v1/me/enrollments",
                      json={"curriculum_key": "mountain_journey", "dialect_id": "gsw-zh"}, headers=headers)
    enr = (await client.get("/api/v1/me/enrollments")).json()["data"][0]
    path = (await client.get(f"/api/v1/me/enrollments/{enr['id']}/path")).json()["data"]
    locked = next(n for n in path["nodes"] if n["state"] == "locked")
    r = await client.post("/api/v1/attempts",
                          json={"mode": "path", "lesson_id": locked["lesson_ref"]["item_id"],
                                "enrollment_id": enr["id"], "node_id": locked["id"], "dialect_id": "gsw-zh"},
                          headers=headers)
    assert r.status_code == 403
