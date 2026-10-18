"""Server-side grading (spec 01 §4). Answer keys never leave the server."""
from __future__ import annotations

import unicodedata
from typing import Any, Dict, List

PASS_THRESHOLD_NUM = 80
PASS_THRESHOLD_DEN = 100


def _normalize_text(value: str, policy: Dict[str, Any]) -> str:
    value = unicodedata.normalize("NFC", value or "")
    value = " ".join(value.split())  # trim + collapse whitespace
    if policy.get("case") == "fold":
        value = value.casefold()
    return value


def grade_exercise(exercise: dict, answer: dict) -> bool:
    """Grade a single exercise against its private grading key.

    ``exercise`` is the full content revision payload+private_grading for the item.
    """
    kind = exercise.get("kind")
    key = exercise.get("private_grading") or {}

    if kind == "mcq":
        return bool(answer.get("choice_id")) and answer.get("choice_id") == key.get("correct_choice_id")

    if kind == "order":
        return list(answer.get("order") or []) == list(key.get("correct_order") or [])

    if kind == "text":
        policy = key.get("normalization", {"case": "fold"})
        given = _normalize_text(str(answer.get("text", "")), policy)
        accepted = [_normalize_text(a, policy) for a in key.get("accepted", [])]
        return given in accepted and given != ""

    return False


def grade_attempt(exercises: List[dict], answers: List[dict], *, missing_policy: str = "incorrect") -> dict:
    """Grade all required exercises. Missing answers scored per policy.

    Returns {correct, total, passed, feedback[]}. ``passed`` compares the raw
    ratio against 80% without pre-rounding (spec 01 §4).
    """
    by_id = {a.get("exercise_id"): a for a in answers}
    total = len(exercises)
    correct = 0
    feedback: List[dict] = []
    for ex in exercises:
        ex_id = ex.get("item_id")
        answer = by_id.get(ex_id)
        is_correct = False
        if answer is not None:
            is_correct = grade_exercise(ex, answer)
        elif missing_policy != "incorrect":
            is_correct = False
        if is_correct:
            correct += 1
        feedback.append({
            "exercise_id": ex_id,
            "correct": is_correct,
            "objective_ids": ex.get("objective_ids", []),
        })
    # 80% compare without rounding: correct/total >= 80/100.
    passed = total > 0 and (correct * PASS_THRESHOLD_DEN) >= (PASS_THRESHOLD_NUM * total)
    return {"correct": correct, "total": total, "passed": passed, "feedback": feedback}
