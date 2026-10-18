"""Learning engine: enrollment, attempts, grading, reviews, rewards (spec 01/02)."""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional

from app.common.errors import bad_request, conflict, forbidden, not_found
from app.common.ids import new_id
from app.common.serialize import jsonable
from app.common.timeutil import local_day, utcnow
from app.content.config_store import get_published_config
from app.db.client import get_db
from app.db.tx import in_transaction
from app.learning import grading

REVIEW_INTERVALS = [1, 3, 7, 14, 30]


# --------------------------------------------------------------------------- #
# Curriculum & enrollment                                                      #
# --------------------------------------------------------------------------- #
async def list_curricula(dialect_id: Optional[str] = None) -> List[dict]:
    db = get_db()
    query: dict = {"status": "published"}
    if dialect_id:
        query["dialect_id"] = dialect_id
    cursor = db["curriculum_releases"].find(query).sort("release_number", -1)
    out = []
    async for r in cursor:
        out.append({
            "release_id": r["_id"], "curriculum_key": r["curriculum_key"],
            "dialect_id": r["dialect_id"], "release_number": r["release_number"],
            "stages": [_stage_public(s) for s in r.get("stages", [])],
            "provenance": r.get("provenance"),
        })
    return out


def _stage_public(stage: dict) -> dict:
    return {
        "id": stage["id"], "sequence": stage.get("sequence"), "name": stage.get("name"),
        "landmark": stage.get("landmark"), "outcomes": stage.get("outcomes", []),
        "status": stage.get("status", "available"),
    }


async def _active_release(curriculum_key: str, dialect_id: str) -> Optional[dict]:
    db = get_db()
    return await db["curriculum_releases"].find_one(
        {"curriculum_key": curriculum_key, "dialect_id": dialect_id, "status": "published"},
        sort=[("release_number", -1)],
    )


async def enroll(user_id: str, curriculum_key: str, dialect_id: str) -> dict:
    db = get_db()
    release = await _active_release(curriculum_key, dialect_id)
    if not release:
        raise not_found("No published curriculum release for this dialect.")
    now = utcnow()
    existing = await db["enrollments"].find_one(
        {"user_id": user_id, "curriculum_key": curriculum_key, "dialect_id": dialect_id}
    )
    if existing:
        return _enrollment_public(existing)

    nodes = release.get("nodes", [])
    first_required = next((n for n in nodes if n.get("required") and not n.get("prerequisite_node_ids")), None)
    total_required = sum(1 for n in nodes if n.get("required"))
    doc = {
        "_id": new_id(), "user_id": user_id, "curriculum_key": curriculum_key,
        "dialect_id": dialect_id, "release_id": release["_id"], "status": "active",
        "current_node_id": first_required["id"] if first_required else None,
        "projection": {"completed_count": 0, "total_required": total_required, "earned_xp": 0},
        "created_at": now, "updated_at": now, "version": 1,
    }
    await db["enrollments"].insert_one(doc)
    return _enrollment_public(doc)


def _enrollment_public(e: dict) -> dict:
    return {
        "id": e["_id"], "curriculum_key": e["curriculum_key"], "dialect_id": e["dialect_id"],
        "release_id": e["release_id"], "status": e["status"],
        "current_node_id": e.get("current_node_id"), "projection": e.get("projection", {}),
    }


async def list_enrollments(user_id: str) -> List[dict]:
    db = get_db()
    cursor = db["enrollments"].find({"user_id": user_id})
    return [_enrollment_public(e) async for e in cursor]


async def _node_states(enrollment: dict, release: dict) -> Dict[str, dict]:
    """Compute node state + reason for every node in the release."""
    db = get_db()
    progress = {
        p["node_id"]: p async for p in db["node_progress"].find({"enrollment_id": enrollment["_id"]})
    }
    states: Dict[str, dict] = {}
    for node in release.get("nodes", []):
        nid = node["id"]
        p = progress.get(nid)
        if p and p.get("state") == "completed":
            states[nid] = {"state": "completed", "reason": "Completed",
                           "review_due": p.get("review_due", False)}
            continue
        prereqs = node.get("prerequisite_node_ids", [])
        unmet = [pr for pr in prereqs if (progress.get(pr) or {}).get("state") != "completed"]
        if node.get("kind") == "checkpoint":
            # Opens when all required lessons in its stage are completed.
            stage = next((s for s in release.get("stages", []) if s["id"] == node.get("stage_id")), {})
            req = stage.get("required_node_ids", [])
            unmet = [r for r in req if (progress.get(r) or {}).get("state") != "completed"]
        if not unmet:
            states[nid] = {"state": "available", "reason": "Ready to start", "review_due": False}
        else:
            states[nid] = {"state": "locked",
                           "reason": f"Complete {len(unmet)} prerequisite(s) first",
                           "review_due": False}
    return states


async def enrollment_path(user_id: str, enrollment_id: str) -> dict:
    db = get_db()
    enrollment = await db["enrollments"].find_one({"_id": enrollment_id, "user_id": user_id})
    if not enrollment:
        raise not_found("Enrollment not found.")
    release = await db["curriculum_releases"].find_one({"_id": enrollment["release_id"]})
    states = await _node_states(enrollment, release)
    nodes = []
    for node in release.get("nodes", []):
        st = states.get(node["id"], {})
        nodes.append({
            "id": node["id"], "stage_id": node.get("stage_id"), "kind": node.get("kind"),
            "title": node.get("title"), "required": node.get("required", False),
            "lesson_ref": node.get("lesson_ref"), "layout": node.get("layout"),
            "prerequisite_node_ids": node.get("prerequisite_node_ids", []),
            "state": st.get("state"), "reason": st.get("reason"), "review_due": st.get("review_due"),
        })
    return {
        "enrollment": _enrollment_public(enrollment),
        "release_id": release["_id"], "dialect_id": release["dialect_id"],
        "provenance": release.get("provenance"),
        "stages": [_stage_public(s) for s in release.get("stages", [])],
        "nodes": nodes,
    }


# --------------------------------------------------------------------------- #
# Lessons & attempts                                                           #
# --------------------------------------------------------------------------- #
async def _published_lesson(lesson_item_id: str) -> Optional[dict]:
    db = get_db()
    item = await db["content_items"].find_one({"_id": lesson_item_id, "status": "published"})
    if not item:
        return None
    revision = await db["content_revisions"].find_one(
        {"item_id": lesson_item_id, "revision": item.get("published_revision", 1)}
    )
    return {"item": item, "revision": revision} if revision else None


async def get_lesson(lesson_item_id: str, support_language: str = "en") -> dict:
    """Study payload only — never includes answer keys."""
    from app.content.service import resolve_dialogue

    lesson = await _published_lesson(lesson_item_id)
    if not lesson:
        raise not_found("Lesson not found.")
    payload = lesson["revision"]["payload"]
    db = get_db()

    dialogues = []
    for did in payload.get("dialogue_item_ids", []):
        ditem = await db["content_items"].find_one({"_id": did, "status": "published"})
        if ditem:
            dialogues.append(await resolve_dialogue(ditem, support_language))

    exercises = []
    for ex_id in payload.get("selected_exercise_ids", []):
        ex = await _published_lesson(ex_id)
        if ex:
            exercises.append(_exercise_public(ex["item"]["_id"], ex["revision"]))

    return {
        "id": lesson_item_id, "title": payload.get("title"),
        "estimated_duration_min": payload.get("estimated_duration_min", 10),
        "steps": payload.get("step_definitions", []),
        "objective_ids": payload.get("objective_ids", []),
        "dialect_verified": payload.get("dialect_verified", False),
        "dialogues": dialogues, "exercises": exercises,
    }


def _exercise_public(item_id: str, revision: dict) -> dict:
    """Public exercise view — choices without the correct answer flag."""
    payload = revision["payload"]
    return {
        "id": item_id, "kind": payload.get("kind"), "prompt": payload.get("prompt"),
        "choices": [{"id": c["id"], "text": c["text"]} for c in payload.get("choices", [])],
        "chunks": payload.get("chunks", []),
        "objective_ids": payload.get("objective_ids", []),
        "context": payload.get("context"),
    }


async def _load_gradable_exercises(exercise_item_ids: List[str]) -> List[dict]:
    """Load exercises with private grading — server-only."""
    out = []
    for ex_id in exercise_item_ids:
        ex = await _published_lesson(ex_id)
        if ex:
            payload = ex["revision"]["payload"]
            out.append({
                "item_id": ex_id,
                "kind": payload.get("kind"),
                "objective_ids": payload.get("objective_ids", []),
                "private_grading": ex["revision"].get("private_grading") or {},
            })
    return out


async def create_attempt(user_id: str, *, mode: str, lesson_id: Optional[str] = None,
                         enrollment_id: Optional[str] = None, node_id: Optional[str] = None,
                         dialect_id: str = "gsw-zh") -> dict:
    db = get_db()
    if mode not in ("path", "practice", "review", "placement"):
        raise bad_request("Invalid attempt mode.")

    grading_cfg = await get_published_config("grading")

    if mode in ("path", "practice"):
        if not lesson_id:
            raise bad_request("lesson_id is required.")
        lesson = await _published_lesson(lesson_id)
        if not lesson:
            raise not_found("Lesson not found.")
        payload = lesson["revision"]["payload"]
        exercise_ids = list(payload.get("selected_exercise_ids", []))
        content_ref = {"item_id": lesson_id, "revision": lesson["revision"]["revision"]}

        if mode == "path":
            if not (enrollment_id and node_id):
                raise bad_request("Path attempts require enrollment_id and node_id.")
            enrollment = await db["enrollments"].find_one({"_id": enrollment_id, "user_id": user_id})
            if not enrollment:
                raise not_found("Enrollment not found.")
            release = await db["curriculum_releases"].find_one({"_id": enrollment["release_id"]})
            states = await _node_states(enrollment, release)
            st = states.get(node_id, {})
            if st.get("state") not in ("available", "completed"):
                raise forbidden(f"Node is not available: {st.get('reason')}", "NODE_LOCKED")
    elif mode == "review":
        exercise_ids = await _due_review_exercise_ids(user_id, dialect_id)
        content_ref = None
        if not exercise_ids:
            raise conflict("No reviews are due right now.", "NO_REVIEWS_DUE")
    else:  # placement
        exercise_ids = []
        content_ref = None

    doc = {
        "_id": new_id(), "user_id": user_id, "dialect_id": dialect_id, "mode": mode,
        "enrollment_id": enrollment_id, "node_id": node_id, "content_ref": content_ref,
        "grading_config_ref": {"key": "grading", "version": (grading_cfg or {}).get("version")},
        "selected_exercises": exercise_ids, "seed": new_id(),
        "answers": [], "acknowledged_steps": [], "state": "in_progress",
        "score_correct": None, "score_total": None, "passed": None,
        "started_at": utcnow(), "submitted_at": None, "version": 1,
    }
    await db["attempts"].insert_one(doc)
    return await _attempt_runner(doc)


async def _attempt_runner(attempt: dict, support_language: str = "en") -> dict:
    """Runner view: exercises WITHOUT answer keys."""
    exercises = []
    for ex_id in attempt.get("selected_exercises", []):
        ex = await _published_lesson(ex_id)
        if ex:
            exercises.append(_exercise_public(ex["item"]["_id"], ex["revision"]))
    return {
        "id": attempt["_id"], "mode": attempt["mode"], "state": attempt["state"],
        "content_ref": attempt.get("content_ref"), "node_id": attempt.get("node_id"),
        "enrollment_id": attempt.get("enrollment_id"), "version": attempt.get("version", 1),
        "exercises": exercises,
        "score": None if attempt["state"] == "in_progress" else {
            "correct": attempt.get("score_correct"), "total": attempt.get("score_total")},
        "passed": attempt.get("passed"),
    }


async def get_attempt(user_id: str, attempt_id: str) -> dict:
    db = get_db()
    attempt = await db["attempts"].find_one({"_id": attempt_id, "user_id": user_id})
    if not attempt:
        raise not_found("Attempt not found.")
    return await _attempt_runner(attempt)


async def save_answers(user_id: str, attempt_id: str, *, attempt_version: int,
                       answers: List[dict], acknowledged_steps: List[str]) -> dict:
    db = get_db()
    attempt = await db["attempts"].find_one({"_id": attempt_id, "user_id": user_id})
    if not attempt:
        raise not_found("Attempt not found.")
    if attempt["state"] != "in_progress":
        raise conflict("Attempt already submitted.", "ATTEMPT_SUBMITTED")
    if attempt.get("version", 1) != attempt_version:
        raise conflict("Attempt was modified elsewhere.", "VERSION_CONFLICT")
    result = await db["attempts"].update_one(
        {"_id": attempt_id, "version": attempt_version},
        {"$set": {"answers": answers, "acknowledged_steps": acknowledged_steps},
         "$inc": {"version": 1}},
    )
    if result.modified_count != 1:
        raise conflict("Attempt was modified elsewhere.", "VERSION_CONFLICT")
    fresh = await db["attempts"].find_one({"_id": attempt_id})
    return {"id": attempt_id, "version": fresh["version"]}


async def submit_attempt(user_id: str, attempt_id: str, *, attempt_version: int,
                         answers: List[dict], acknowledged_steps: List[str],
                         idempotency_key: Optional[str] = None) -> dict:
    db = get_db()

    # Idempotency: same key+body returns the original; same key/different body -> 409.
    import hashlib as _hashlib
    import json as _json
    request_hash = _hashlib.sha256(
        _json.dumps({"answers": answers, "ack": acknowledged_steps}, sort_keys=True, default=str).encode()
    ).hexdigest()
    if idempotency_key:
        receipt = await db["idempotency_receipts"].find_one(
            {"user_id": user_id, "scope": "attempt_submit", "key": idempotency_key}
        )
        if receipt:
            if receipt.get("request_hash") not in (request_hash, attempt_id):
                raise conflict("Idempotency key reused with a different body.", "IDEMPOTENCY_CONFLICT")
            return receipt["response"]

    attempt = await db["attempts"].find_one({"_id": attempt_id, "user_id": user_id})
    if not attempt:
        raise not_found("Attempt not found.")
    if attempt["state"] == "submitted":
        return await _finished_result(attempt)

    grading_cfg = await get_published_config("grading") or {}
    reward_cfg = await get_published_config("rewards") or {}
    missing_policy = grading_cfg.get("missing_answer_policy", "incorrect")

    gradables = await _load_gradable_exercises(attempt.get("selected_exercises", []))
    graded = grading.grade_attempt(gradables, answers, missing_policy=missing_policy)

    user = await db["users"].find_one({"_id": user_id})
    tz = (user.get("preferences", {}) or {}).get("timezone", "Europe/Zurich")
    now = utcnow()
    today = local_day(now, tz)

    outcome = {"awarded_xp": 0, "completed_node_id": None, "next_node_id": None,
               "finalized_elsewhere": False}

    async def _txn(s):
        # Reset per-attempt (with_transaction may retry this callback).
        outcome["awarded_xp"] = 0
        outcome["completed_node_id"] = None
        outcome["next_node_id"] = None
        outcome["finalized_elsewhere"] = False

        upd = await db["attempts"].update_one(
            {"_id": attempt_id, "state": "in_progress"},
            {"$set": {
                "state": "submitted", "answers": answers,
                "acknowledged_steps": acknowledged_steps,
                "score_correct": graded["correct"], "score_total": graded["total"],
                "passed": graded["passed"], "submitted_at": now,
            }, "$inc": {"version": 1}},
            session=s,
        )
        if upd.modified_count != 1:
            outcome["finalized_elsewhere"] = True
            return

        # Objective reviews (advance at most once per objective per local day).
        await _update_objective_reviews(
            db, s, user_id, attempt["dialect_id"], graded["feedback"], today, now, reward_cfg
        )

        # Path completion + rewards.
        if attempt["mode"] == "path" and graded["passed"] and attempt.get("node_id"):
            enrollment = await db["enrollments"].find_one(
                {"_id": attempt["enrollment_id"]}, session=s
            )
            release = await db["curriculum_releases"].find_one(
                {"_id": enrollment["release_id"]}, session=s
            )
            node = next((n for n in release["nodes"] if n["id"] == attempt["node_id"]), {})
            is_checkpoint = node.get("kind") == "checkpoint"

            np = await db["node_progress"].find_one(
                {"enrollment_id": enrollment["_id"], "node_id": attempt["node_id"]}, session=s
            )
            first_completion = not (np and np.get("state") == "completed")
            await db["node_progress"].update_one(
                {"enrollment_id": enrollment["_id"], "node_id": attempt["node_id"]},
                {"$set": {"state": "completed", "latest_attempt_id": attempt_id,
                          "completed_at": now},
                 "$setOnInsert": {"_id": new_id(), "enrollment_id": enrollment["_id"],
                                  "node_id": attempt["node_id"],
                                  "first_passed_attempt_id": attempt_id, "review_due": False,
                                  "version": 1}},
                upsert=True, session=s,
            )
            outcome["completed_node_id"] = attempt["node_id"]

            if first_completion:
                xp_amount = (reward_cfg.get("checkpoint_first_pass_xp", 50) if is_checkpoint
                             else reward_cfg.get("lesson_first_completion_xp", 20))
                source_key = f"{'checkpoint' if is_checkpoint else 'lesson'}:{enrollment['_id']}:{attempt['node_id']}"
                awarded = await _grant_reward(
                    db, s, user_id, enrollment, attempt["dialect_id"], source_key,
                    "checkpoint" if is_checkpoint else "lesson", xp_amount, today, reward_cfg,
                )
                outcome["awarded_xp"] += awarded

            states = await _node_states_in_session(db, s, enrollment, release)
            outcome["next_node_id"] = _pick_next_node(release, states)
            completed_count = sum(1 for st in states.values() if st == "completed")
            total_required = sum(1 for n in release["nodes"] if n.get("required"))
            earned = await _sum_xp(db, s, user_id, enrollment["dialect_id"])
            await db["enrollments"].update_one(
                {"_id": enrollment["_id"]},
                {"$set": {"current_node_id": outcome["next_node_id"] or enrollment.get("current_node_id"),
                          "projection": {"completed_count": completed_count,
                                         "total_required": total_required, "earned_xp": earned},
                          "updated_at": now},
                 "$inc": {"version": 1}},
                session=s,
            )

        # Review-session reward (qualifying: >=5 items, >=80%).
        if attempt["mode"] == "review" and graded["total"] >= reward_cfg.get("review_min_items", 5):
            ratio_ok = graded["correct"] * 100 >= reward_cfg.get("review_min_accuracy", 80) * graded["total"]
            if ratio_ok:
                source_key = f"review:{attempt['dialect_id']}:{today}:{attempt_id}"
                awarded = await _grant_capped_review_reward(
                    db, s, user_id, attempt["dialect_id"], source_key, today, reward_cfg
                )
                outcome["awarded_xp"] += awarded

        # Activity day (qualifying pass or review).
        if graded["passed"] or attempt["mode"] == "review":
            await db["activity_days"].update_one(
                {"user_id": user_id, "local_date": today},
                {"$setOnInsert": {"_id": new_id(), "user_id": user_id, "local_date": today,
                                  "timezone_at_award": tz, "created_at": now},
                 "$addToSet": {"qualifying_attempt_ids": attempt_id},
                 "$inc": {"xp_total": outcome["awarded_xp"]}},
                upsert=True, session=s,
            )

        # Audit.
        await db["audit_log"].insert_one({
            "_id": new_id(), "actor_user_id": user_id, "action": "attempt.submit",
            "target_type": "attempt", "target_id": attempt_id,
            "reason": None, "created_at": now,
        }, session=s)

    await in_transaction(_txn)

    if outcome["finalized_elsewhere"]:
        fresh = await db["attempts"].find_one({"_id": attempt_id})
        return await _finished_result(fresh)

    awarded_xp = outcome["awarded_xp"]
    completed_node_id = outcome["completed_node_id"]
    next_node_id = outcome["next_node_id"]

    result = {
        "attempt_id": attempt_id,
        "score": {"correct": graded["correct"], "total": graded["total"]},
        "passed": graded["passed"],
        "completed_node_id": completed_node_id,
        "awarded_xp": awarded_xp,
        "next_node_id": next_node_id,
        "feedback": [{"exercise_id": f["exercise_id"], "correct": f["correct"]} for f in graded["feedback"]],
        "grading_policy": {"pass_threshold": "80%", "missing_answer_policy": missing_policy},
    }

    if idempotency_key:
        await db["idempotency_receipts"].update_one(
            {"user_id": user_id, "scope": "attempt_submit", "key": idempotency_key},
            {"$setOnInsert": {
                "_id": new_id(), "user_id": user_id, "scope": "attempt_submit",
                "key": idempotency_key, "request_hash": request_hash,
                "response_status": 200, "response": result, "created_at": now,
                "expires_at": now + timedelta(days=7),
            }}, upsert=True,
        )
    return result


async def _finished_result(attempt: dict) -> dict:
    return {
        "attempt_id": attempt["_id"],
        "score": {"correct": attempt.get("score_correct"), "total": attempt.get("score_total")},
        "passed": attempt.get("passed"),
        "completed_node_id": attempt.get("node_id") if attempt.get("passed") else None,
        "awarded_xp": 0,
        "next_node_id": None,
        "feedback": [],
        "grading_policy": {"pass_threshold": "80%"},
    }


async def _grant_reward(db, s, user_id, enrollment, dialect_id, source_key, kind, amount, today, reward_cfg) -> int:
    existing = await db["reward_ledger"].find_one({"user_id": user_id, "source_key": source_key}, session=s)
    if existing:
        return 0
    await db["reward_ledger"].insert_one({
        "_id": new_id(), "user_id": user_id, "enrollment_id": enrollment["_id"],
        "dialect_id": dialect_id, "source_key": source_key, "kind": kind,
        "amount_xp": amount, "rule_ref": {"key": "rewards", "version": reward_cfg.get("version")},
        "event_day": today, "created_at": utcnow(),
    }, session=s)
    return amount


async def _grant_capped_review_reward(db, s, user_id, dialect_id, source_key, today, reward_cfg) -> int:
    existing = await db["reward_ledger"].find_one({"user_id": user_id, "source_key": source_key}, session=s)
    if existing:
        return 0
    # Enforce daily review XP cap.
    cap = reward_cfg.get("review_daily_cap_xp", 20)
    day_total = 0
    cursor = db["reward_ledger"].find({"user_id": user_id, "kind": "review", "event_day": today}, session=s)
    async for r in cursor:
        day_total += r.get("amount_xp", 0)
    amount = reward_cfg.get("review_session_xp", 5)
    if day_total + amount > cap:
        amount = max(0, cap - day_total)
    if amount <= 0:
        return 0
    await db["reward_ledger"].insert_one({
        "_id": new_id(), "user_id": user_id, "enrollment_id": None, "dialect_id": dialect_id,
        "source_key": source_key, "kind": "review", "amount_xp": amount,
        "rule_ref": {"key": "rewards", "version": reward_cfg.get("version")},
        "event_day": today, "created_at": utcnow(),
    }, session=s)
    return amount


async def _sum_xp(db, s, user_id, dialect_id) -> int:
    total = 0
    cursor = db["reward_ledger"].find({"user_id": user_id, "dialect_id": dialect_id}, session=s)
    async for r in cursor:
        total += r.get("amount_xp", 0)
    return total


async def _update_objective_reviews(db, s, user_id, dialect_id, feedback, today, now, reward_cfg):
    intervals = reward_cfg.get("intervals_days", REVIEW_INTERVALS)
    # Flatten objective -> correctness (an objective is correct only if all its items correct).
    obj_results: Dict[str, bool] = {}
    for f in feedback:
        for oid in f.get("objective_ids", []):
            obj_results[oid] = obj_results.get(oid, True) and f["correct"]
    for objective_id, correct in obj_results.items():
        op = await db["objective_progress"].find_one(
            {"user_id": user_id, "dialect_id": dialect_id, "objective_id": objective_id}, session=s
        )
        if op is None:
            op = {
                "_id": new_id(), "user_id": user_id, "dialect_id": dialect_id,
                "objective_id": objective_id, "practice_count": 0,
                "distinct_success_days": [], "review_stage": 0, "last_result": None,
                "last_success_day": None, "due_at": None, "updated_at": now, "version": 1,
            }
            await db["objective_progress"].insert_one(op, session=s)

        advanced_today = op.get("last_success_day") == today
        updates: Dict[str, Any] = {"practice_count": op.get("practice_count", 0) + 1,
                                   "last_result": "correct" if correct else "incorrect",
                                   "updated_at": now}
        if correct:
            if not advanced_today:
                stage = min(op.get("review_stage", 0) + 1, len(intervals))
                interval = intervals[min(stage - 1, len(intervals) - 1)]
                updates["review_stage"] = stage
                updates["last_success_day"] = today
                updates["due_at"] = now + timedelta(days=interval)
                days = set(op.get("distinct_success_days", []))
                days.add(today)
                updates["distinct_success_days"] = sorted(days)[-30:]
        else:
            updates["review_stage"] = 0
            updates["due_at"] = now + timedelta(days=1)
        await db["objective_progress"].update_one(
            {"_id": op["_id"]}, {"$set": updates, "$inc": {"version": 1}}, session=s
        )


async def _node_states_in_session(db, s, enrollment, release) -> Dict[str, str]:
    progress = {}
    cursor = db["node_progress"].find({"enrollment_id": enrollment["_id"]}, session=s)
    async for p in cursor:
        progress[p["node_id"]] = p.get("state")
    states: Dict[str, str] = {}
    for node in release["nodes"]:
        nid = node["id"]
        if progress.get(nid) == "completed":
            states[nid] = "completed"
            continue
        if node.get("kind") == "checkpoint":
            stage = next((st for st in release["stages"] if st["id"] == node.get("stage_id")), {})
            req = stage.get("required_node_ids", [])
            unmet = [r for r in req if progress.get(r) != "completed"]
        else:
            unmet = [p for p in node.get("prerequisite_node_ids", []) if progress.get(p) != "completed"]
        states[nid] = "available" if not unmet else "locked"
    return states


def _pick_next_node(release, states: Dict[str, str]) -> Optional[str]:
    for node in release["nodes"]:
        if states.get(node["id"]) == "available":
            return node["id"]
    return None


async def _due_review_exercise_ids(user_id: str, dialect_id: str, limit: int = 8) -> List[str]:
    db = get_db()
    now = utcnow()
    cursor = db["objective_progress"].find(
        {"user_id": user_id, "dialect_id": dialect_id, "due_at": {"$lte": now}}
    ).sort("due_at", 1).limit(limit)
    objective_ids = [op["objective_id"] async for op in cursor]
    if not objective_ids:
        return []
    # Find exercises covering these objectives.
    ex_cursor = db["content_items"].find(
        {"kind": "exercise", "status": "published"}
    )
    exercise_ids: List[str] = []
    async for item in ex_cursor:
        rev = await db["content_revisions"].find_one(
            {"item_id": item["_id"], "revision": item.get("published_revision", 1)}
        )
        if rev and set(rev["payload"].get("objective_ids", [])).intersection(objective_ids):
            exercise_ids.append(item["_id"])
        if len(exercise_ids) >= limit:
            break
    return exercise_ids


async def due_reviews(user_id: str, dialect_id: str) -> dict:
    db = get_db()
    now = utcnow()
    cursor = db["objective_progress"].find(
        {"user_id": user_id, "dialect_id": dialect_id, "due_at": {"$lte": now}}
    ).sort("due_at", 1).limit(50)
    objectives = [{"objective_id": op["objective_id"], "review_stage": op.get("review_stage"),
                   "due_at": jsonable(op.get("due_at"))} async for op in cursor]
    exercise_ids = await _due_review_exercise_ids(user_id, dialect_id)
    return {"due_count": len(objectives), "objectives": objectives,
            "has_session": len(exercise_ids) > 0}


async def progress_summary(user_id: str, dialect_id: str) -> dict:
    db = get_db()
    now = utcnow()
    attempts_total = await db["attempts"].count_documents(
        {"user_id": user_id, "dialect_id": dialect_id, "state": "submitted"}
    )
    passed = await db["attempts"].count_documents(
        {"user_id": user_id, "dialect_id": dialect_id, "state": "submitted", "passed": True}
    )
    xp = 0
    cursor = db["reward_ledger"].find({"user_id": user_id, "dialect_id": dialect_id})
    async for r in cursor:
        xp += r.get("amount_xp", 0)
    due = await db["objective_progress"].count_documents(
        {"user_id": user_id, "dialect_id": dialect_id, "due_at": {"$lte": now}}
    )
    remembered = await db["objective_progress"].count_documents(
        {"user_id": user_id, "dialect_id": dialect_id, "review_stage": {"$gte": 3}}
    )
    streak = await _current_streak(user_id)
    return {
        "dialect_id": dialect_id, "attempts": attempts_total, "passed": passed,
        "earned_xp": xp, "due_reviews": due, "remembered_objectives": remembered,
        "streak_days": streak,
    }


async def _current_streak(user_id: str) -> int:
    db = get_db()
    cursor = db["activity_days"].find({"user_id": user_id}).sort("local_date", -1).limit(400)
    days = [d["local_date"] async for d in cursor]
    if not days:
        return 0
    from datetime import date
    streak = 0
    expected = date.fromisoformat(days[0])
    today = utcnow().date()
    # Streak is only "current" if the latest qualifying day is today or yesterday.
    if (today - expected).days > 1:
        return 0
    day_set = set(days)
    cursor_day = expected
    while cursor_day.isoformat() in day_set:
        streak += 1
        cursor_day = cursor_day.fromordinal(cursor_day.toordinal() - 1)
    return streak
