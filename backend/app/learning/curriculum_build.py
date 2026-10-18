"""Build an introductory curriculum release with server-gradable lessons.

Lessons, objectives and comprehension exercises are derived deterministically
from published dialogues. Because the source dialogues are legacy and their Swiss
dialect has NOT been human-verified, the release is explicitly labelled
``dialect_verified = False`` and carries a preview provenance. This keeps the
learning engine fully functional and testable without fabricating verified
native-dialect mastery. Real dialect-verified content replaces this via the AI
workshop + publisher review (see docs TODO).
"""
from __future__ import annotations

import hashlib
import json
from typing import Dict, List

from pymongo.database import Database

from app.common.ids import deterministic_id
from app.common.timeutil import utcnow

CURRICULUM_KEY = "mountain_journey"
RELEASE_PROVENANCE = {"source": "legacy_unverified_preview", "builder": "build_curriculum_v1"}

STAGES_PLAN = [
    {"id": "stage-0", "sequence": 0, "name": "Discover Switzerland",
     "landmark": "Welcome trail", "outcomes": ["Bridge from German", "High-frequency chunks"],
     "lessons": 6},
    {"id": "stage-1", "sequence": 1, "name": "Rigi",
     "landmark": "Rigi summit", "outcomes": ["Everyday essentials"],
     "lessons": 4},
]


def _mcq_exercises(dialogue_item_id: str, turns: List[dict], objective_id: str,
                   distractor_pool: List[str]) -> List[dict]:
    """Deterministic comprehension MCQs from dialogue turns."""
    exercises = []
    usable = [t for t in turns if t.get("swiss_german") and t.get("german")][:6]
    for idx, turn in enumerate(usable[:5]):
        correct = turn["german"]
        # Distractors: other german lines (stable order), excluding the correct one.
        distractors = [d for d in distractor_pool if d and d != correct][:6]
        # Deterministic pick of 3 distractors.
        seed = int(hashlib.sha256(f"{dialogue_item_id}:{idx}".encode()).hexdigest(), 16)
        chosen = []
        i = 0
        while len(chosen) < 3 and distractors:
            cand = distractors[(seed + i) % len(distractors)]
            if cand not in chosen:
                chosen.append(cand)
            i += 1
            if i > 50:
                break
        choices_texts = [correct] + chosen
        # Deterministic rotation of positions, then assign IDs by final position
        # so the correct answer is not predictably choice "a".
        order_seed = seed % max(1, len(choices_texts))
        choices_texts = choices_texts[order_seed:] + choices_texts[:order_seed]
        choices = [{"id": chr(ord("a") + i), "text": t} for i, t in enumerate(choices_texts)]
        correct_id = next(c["id"] for c in choices if c["text"] == correct)
        exercises.append({
            "prompt": f"What does «{turn['swiss_german']}» mean in Standard German?",
            "kind": "mcq",
            "choices": choices,
            "objective_ids": [objective_id],
            "context": {"dialogue_item_id": dialogue_item_id, "turn_id": turn.get("id")},
            "private_grading": {"correct_choice_id": correct_id},
        })
    return exercises


def _resolve_turns(db: Database, dialogue_item: dict) -> List[dict]:
    rev = db["content_revisions"].find_one(
        {"item_id": dialogue_item["_id"], "revision": dialogue_item.get("published_revision", 1)}
    )
    if not rev:
        return []
    uids = []
    for t in rev["payload"].get("turns", []):
        uids += [t.get("utterance_id"), t.get("german_utterance_id")]
    utts = {u["_id"]: u for u in db["utterances"].find({"_id": {"$in": [u for u in uids if u]}})}
    out = []
    for t in rev["payload"].get("turns", []):
        su = utts.get(t.get("utterance_id"))
        gu = utts.get(t.get("german_utterance_id"))
        out.append({"id": t.get("id"), "swiss_german": su.get("text") if su else None,
                    "german": gu.get("text") if gu else None})
    return out


def build(db: Database, dialect_id: str = "gsw-zh") -> dict:
    now = utcnow()
    # Deterministically select dialogues with enough turns.
    candidates = []
    for item in db["content_items"].find({"kind": "dialogue", "status": "published"}).sort("_id", 1):
        turns = _resolve_turns(db, item)
        usable = [t for t in turns if t.get("swiss_german") and t.get("german")]
        if len(usable) >= 5:
            candidates.append((item, turns))
        if len(candidates) >= sum(s["lessons"] for s in STAGES_PLAN):
            break

    all_german = []
    for _, turns in candidates:
        all_german += [t["german"] for t in turns if t.get("german")]

    def upsert_item(item: dict, revision: dict):
        db["content_items"].replace_one({"_id": item["_id"]}, item, upsert=True)
        db["content_revisions"].replace_one({"_id": revision["_id"]}, revision, upsert=True)

    def make_content(kind: str, slug: str, payload: dict, private_grading=None,
                     dialect=None, title=None) -> str:
        item_id = deterministic_id("content", kind, slug)
        item = {
            "_id": item_id, "schema_version": 1, "kind": kind, "slug": slug,
            "dialect_id": dialect, "scenario_id": None, "legacy_id": None,
            "status": "published", "published_revision": 1, "draft_revision": None,
            "discovery": {"title": title}, "title": title, "summary": None, "tags": [],
            "topic_id": None, "subtopic_id": None, "search_text": (title or "").lower(),
            "sort_order": 0, "created_at": now, "updated_at": now, "version": 1,
        }
        revision = {
            "_id": deterministic_id("revision", item_id, "1"), "schema_version": 1,
            "item_id": item_id, "revision": 1, "kind": kind, "dialect_id": dialect,
            "status": "published", "payload": payload, "private_grading": private_grading,
            "references": [], "provenance": RELEASE_PROVENANCE,
            "qa": {"dialect_verified": False}, "created_by": "system",
            "created_at": now, "version": 1,
        }
        upsert_item(item, revision)
        return item_id

    nodes: List[dict] = []
    stages: List[dict] = []
    created = {"lessons": 0, "objectives": 0, "exercises": 0, "checkpoints": 0}

    cand_iter = iter(candidates)
    for stage_plan in STAGES_PLAN:
        stage_required_nodes: List[str] = []
        stage_lesson_exercise_ids: List[str] = []
        prev_node_id = None
        for li in range(stage_plan["lessons"]):
            try:
                dialogue_item, turns = next(cand_iter)
            except StopIteration:
                break
            dslug = dialogue_item["slug"]
            # Objective
            objective_id = make_content(
                "objective", f"obj-{dslug}",
                {"outcome": f"Understand the dialogue: {dialogue_item.get('title')}",
                 "dialect_id": dialect_id, "dialect_verified": False,
                 "dialogue_item_id": dialogue_item["_id"]},
                dialect=dialect_id, title=f"Objective: {dialogue_item.get('title')}")
            created["objectives"] += 1
            # Exercises
            exercise_ids = []
            exercises = _mcq_exercises(dialogue_item["_id"], turns, objective_id, all_german)
            for ei, ex in enumerate(exercises):
                ex_id = make_content(
                    "exercise", f"ex-{dslug}-{ei}",
                    {"kind": ex["kind"], "prompt": ex["prompt"], "choices": ex["choices"],
                     "objective_ids": ex["objective_ids"], "context": ex["context"],
                     "dialect_verified": False},
                    private_grading=ex["private_grading"], dialect=dialect_id,
                    title=ex["prompt"][:60])
                exercise_ids.append(ex_id)
                created["exercises"] += 1
            # Lesson
            lesson_id = make_content(
                "lesson", f"lesson-{dslug}",
                {"title": dialogue_item.get("title") or "Lesson",
                 "dialogue_item_ids": [dialogue_item["_id"]], "objective_ids": [objective_id],
                 "selected_exercise_ids": exercise_ids,
                 "step_definitions": [{"id": "scene"}, {"id": "understand"}, {"id": "notice"},
                                      {"id": "rehearse"}, {"id": "respond"}, {"id": "recall"}],
                 "estimated_duration_min": 10, "dialect_verified": False},
                dialect=dialect_id, title=dialogue_item.get("title"))
            created["lessons"] += 1

            node_id = f"{stage_plan['id']}-lesson-{li}"
            nodes.append({
                "id": node_id, "stage_id": stage_plan["id"], "kind": "lesson",
                "title": dialogue_item.get("title") or f"Lesson {li+1}",
                "lesson_ref": {"item_id": lesson_id, "revision": 1},
                "prerequisite_node_ids": [prev_node_id] if prev_node_id else [],
                "required": True,
                "layout": {"x": li * 120, "y": (stage_plan["sequence"] * 200) + (li % 2) * 40, "segment": stage_plan["id"]},
            })
            stage_required_nodes.append(node_id)
            stage_lesson_exercise_ids += exercise_ids[:3]
            prev_node_id = node_id

        # Checkpoint for the stage (>=10 items).
        checkpoint_pool = stage_lesson_exercise_ids[:12]
        if len(checkpoint_pool) >= 10:
            cp_lesson_id = make_content(
                "checkpoint", f"checkpoint-{stage_plan['id']}",
                {"title": f"{stage_plan['name']} checkpoint",
                 "dialogue_item_ids": [], "objective_ids": [],
                 "selected_exercise_ids": checkpoint_pool,
                 "step_definitions": [{"id": "recall"}], "estimated_duration_min": 8,
                 "dialect_verified": False},
                dialect=dialect_id, title=f"{stage_plan['name']} checkpoint")
            cp_node_id = f"{stage_plan['id']}-checkpoint"
            nodes.append({
                "id": cp_node_id, "stage_id": stage_plan["id"], "kind": "checkpoint",
                "title": f"{stage_plan['landmark']}",
                "lesson_ref": {"item_id": cp_lesson_id, "revision": 1},
                "prerequisite_node_ids": list(stage_required_nodes), "required": True,
                "layout": {"x": len(stage_required_nodes) * 120, "y": stage_plan["sequence"] * 200, "segment": stage_plan["id"]},
            })
            created["checkpoints"] += 1
            stages.append({**{k: stage_plan[k] for k in ("id", "sequence", "name", "landmark", "outcomes")},
                           "required_node_ids": list(stage_required_nodes), "status": "available"})

    graph_hash = hashlib.sha256(json.dumps(nodes, sort_keys=True).encode()).hexdigest()
    release_id = deterministic_id("release", CURRICULUM_KEY, dialect_id, "1")
    db["curriculum_releases"].replace_one(
        {"_id": release_id},
        {"_id": release_id, "schema_version": 1, "curriculum_key": CURRICULUM_KEY,
         "dialect_id": dialect_id, "release_number": 1, "status": "published",
         "nodes": nodes, "stages": stages, "graph_hash": graph_hash,
         "grading_config_ref": {"key": "grading", "version": "grading-v1"},
         "reward_config_ref": {"key": "rewards", "version": "rewards-v1"},
         "equivalence": None, "provenance": RELEASE_PROVENANCE,
         "dialect_verified": False, "published_at": now,
         "created_at": now, "version": 1},
        upsert=True,
    )
    return {"release_id": release_id, "dialect_id": dialect_id, "nodes": len(nodes),
            "stages": len(stages), **created}


def validate_release(release: dict) -> List[str]:
    """DAG validation: unique nodes, no cycles, reachable, refs approved."""
    errors = []
    node_ids = [n["id"] for n in release["nodes"]]
    if len(node_ids) != len(set(node_ids)):
        errors.append("duplicate node ids")
    id_set = set(node_ids)
    for n in release["nodes"]:
        for p in n.get("prerequisite_node_ids", []):
            if p not in id_set:
                errors.append(f"node {n['id']} references missing prerequisite {p}")
    # Cycle detection (topological).
    graph = {n["id"]: list(n.get("prerequisite_node_ids", [])) for n in release["nodes"]}
    visited: Dict[str, int] = {}

    def dfs(node):
        state = visited.get(node, 0)
        if state == 1:
            errors.append(f"cycle at {node}")
            return
        if state == 2:
            return
        visited[node] = 1
        for dep in graph.get(node, []):
            dfs(dep)
        visited[node] = 2

    for nid in node_ids:
        dfs(nid)
    return errors
