"""Learning API: curricula, enrollments, lessons, attempts, reviews, progress."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel

from app.auth.deps import current_user, require_csrf
from app.learning import service

router = APIRouter(prefix="/api/v1", tags=["learning"])


@router.get("/curricula")
async def get_curricula(dialect_id: Optional[str] = None):
    return {"data": await service.list_curricula(dialect_id)}


class EnrollIn(BaseModel):
    curriculum_key: str
    dialect_id: str


@router.post("/me/enrollments")
async def enroll(payload: EnrollIn, user: dict = Depends(require_csrf)):
    return {"data": await service.enroll(user["_id"], payload.curriculum_key, payload.dialect_id)}


@router.get("/me/enrollments")
async def my_enrollments(user: dict = Depends(current_user)):
    return {"data": await service.list_enrollments(user["_id"])}


@router.get("/me/enrollments/{enrollment_id}/path")
async def enrollment_path(enrollment_id: str, user: dict = Depends(current_user)):
    return {"data": await service.enrollment_path(user["_id"], enrollment_id)}


@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, support_language: str = "en", user: dict = Depends(current_user)):
    return {"data": await service.get_lesson(lesson_id, support_language)}


class AttemptIn(BaseModel):
    mode: str = "path"
    lesson_id: Optional[str] = None
    enrollment_id: Optional[str] = None
    node_id: Optional[str] = None
    dialect_id: str = "gsw-zh"


@router.post("/attempts")
async def create_attempt(payload: AttemptIn, user: dict = Depends(require_csrf)):
    return {"data": await service.create_attempt(
        user["_id"], mode=payload.mode, lesson_id=payload.lesson_id,
        enrollment_id=payload.enrollment_id, node_id=payload.node_id,
        dialect_id=payload.dialect_id,
    )}


@router.get("/attempts/{attempt_id}")
async def get_attempt(attempt_id: str, user: dict = Depends(current_user)):
    return {"data": await service.get_attempt(user["_id"], attempt_id)}


class AnswerItem(BaseModel):
    exercise_id: str
    choice_id: Optional[str] = None
    text: Optional[str] = None
    order: Optional[List[str]] = None


class SaveAnswersIn(BaseModel):
    attempt_version: int
    answers: List[AnswerItem] = []
    acknowledged_steps: List[str] = []


@router.patch("/attempts/{attempt_id}")
async def save_answers(attempt_id: str, payload: SaveAnswersIn, user: dict = Depends(require_csrf)):
    return {"data": await service.save_answers(
        user["_id"], attempt_id, attempt_version=payload.attempt_version,
        answers=[a.model_dump(exclude_none=True) for a in payload.answers],
        acknowledged_steps=payload.acknowledged_steps,
    )}


@router.post("/attempts/{attempt_id}/submit")
async def submit_attempt(attempt_id: str, payload: SaveAnswersIn,
                         user: dict = Depends(require_csrf),
                         idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key")):
    return {"data": await service.submit_attempt(
        user["_id"], attempt_id, attempt_version=payload.attempt_version,
        answers=[a.model_dump(exclude_none=True) for a in payload.answers],
        acknowledged_steps=payload.acknowledged_steps,
        idempotency_key=idempotency_key,
    )}


@router.get("/me/reviews")
async def reviews(dialect_id: str = "gsw-zh", user: dict = Depends(current_user)):
    return {"data": await service.due_reviews(user["_id"], dialect_id)}


@router.get("/me/progress")
async def progress(dialect_id: str = "gsw-zh", user: dict = Depends(current_user)):
    return {"data": await service.progress_summary(user["_id"], dialect_id)}
