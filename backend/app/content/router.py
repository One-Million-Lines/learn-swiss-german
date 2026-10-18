"""Public content & discovery API (spec 04 §2) plus legacy compatibility routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.content import service

router = APIRouter(prefix="/api/v1", tags=["content"])


def _data(obj):
    return {"data": obj}


def _list(items, next_cursor=None, has_more=False):
    return {"data": items, "page": {"next_cursor": next_cursor, "has_more": has_more}}


@router.get("/home")
async def get_home(dialect_id: Optional[str] = None, support_language: str = "en"):
    return _data(await service.home(support_language, dialect_id))


@router.get("/dialects")
async def get_dialects():
    return _list(await service.list_dialects())


@router.get("/topics")
async def get_topics():
    return _list(await service.list_topics())


@router.get("/topics/{id_or_slug}")
async def get_topic(id_or_slug: str):
    return _data(await service.get_topic(id_or_slug))


@router.get("/subtopics/{id_or_slug}")
async def get_subtopic(id_or_slug: str, support_language: str = "en"):
    return _data(await service.get_subtopic(id_or_slug, support_language))


@router.get("/dialogues/{id_or_slug}")
async def get_dialogue(id_or_slug: str, support_language: str = "en", dialect_id: Optional[str] = None):
    return _data(await service.get_dialogue(id_or_slug, support_language))


@router.get("/patterns")
async def get_patterns():
    return _list(await service.list_patterns())


@router.get("/vocabulary")
async def get_vocabulary(topic_id: Optional[str] = None):
    return _list(await service.list_vocabulary(topic_id))


@router.get("/search")
async def get_search(q: str = Query(..., min_length=2), kind: Optional[str] = None, dialect_id: Optional[str] = None):
    return _list(await service.search(q, kind))


@router.get("/daily")
async def get_daily(dialect_id: Optional[str] = None, support_language: str = "en"):
    return _data(await service.daily_selection(support_language))


@router.get("/creators")
async def get_creators():
    return _list(await service.featured_creators(limit=50))


# --------------------------------------------------------------------------- #
# Legacy compatibility: preserve the old /content/* shape, backed by MongoDB.  #
# These keep existing deep links and old frontend builds working.              #
# --------------------------------------------------------------------------- #
legacy_router = APIRouter(prefix="/content", tags=["content-legacy"])


@legacy_router.get("/topics")
async def legacy_topics():
    topics = await service.list_topics()
    return {"topics": [{**t, "subtopicCount": t["subtopic_count"]} for t in topics]}


@legacy_router.get("/topics/{topic_id}")
async def legacy_topic(topic_id: str):
    t = await service.get_topic(topic_id)
    return {**t, "subtopicCount": t["subtopic_count"]}


@legacy_router.get("/subtopics/{subtopic_id}")
async def legacy_subtopic(subtopic_id: str):
    s = await service.get_subtopic(subtopic_id)
    # Map to legacy field names.
    return {
        "id": s["id"], "topicId": s["topic_id"], "title": s["title"],
        "description": s["description"],
        "dialogues": [_legacy_dialogue(d) for d in s["dialogues"]],
    }


@legacy_router.get("/patterns")
async def legacy_patterns():
    return {"patterns": await service.list_patterns()}


@legacy_router.get("/vocabulary")
async def legacy_vocabulary(topic_id: Optional[str] = None):
    groups = await service.list_vocabulary(topic_id)
    return {"vocabulary": [{"id": g["id"], "topicId": g["topic_id"], "title": g["title"], "words": g["words"]} for g in groups]}


@legacy_router.get("/daily-phrase")
async def legacy_daily_phrase():
    daily = await service.daily_selection("en")
    phrase = daily.get("phrase") or {}
    return {"phrase": {"swissGerman": phrase.get("swiss_german"), "german": phrase.get("german"),
                       "english": phrase.get("translation"), "topic": phrase.get("topic")},
            "date": daily["date"]}


@legacy_router.get("/daily-dialogue")
async def legacy_daily_dialogue():
    daily = await service.daily_selection("en")
    d = daily.get("dialogue")
    if not d:
        return {"dialogue": None, "date": daily["date"]}
    return {"dialogue": {**_legacy_dialogue(d), "subtopicId": d.get("subtopic_id"),
                         "subtopicTitle": d.get("title")}, "date": daily["date"]}


def _legacy_dialogue(d: dict) -> dict:
    return {
        "id": d.get("legacy_id") or d["id"],
        "level": d.get("level"),
        "title": d.get("title"),
        "situation": d.get("situation"),
        "lines": [
            {"speaker": t["speaker"], "swissGerman": t["swiss_german"], "german": t["german"],
             "english": t["translation"], "spanish": t.get("translation")}
            for t in d.get("turns", [])
        ],
        "differences": [
            {"swissGerman": x["swiss_german"], "german": x["german"], "explanation": x["explanation"]}
            for x in d.get("differences", [])
        ],
        "keyPhrases": [
            {"swissGerman": k["swiss_german"], "german": k["german"], "english": k["translation"]}
            for k in d.get("key_phrases", [])
        ],
    }
