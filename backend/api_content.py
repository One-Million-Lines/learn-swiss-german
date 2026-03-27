import datetime
from fastapi import APIRouter, HTTPException
from data.content import TOPICS, SUBTOPICS, PATTERNS, VOCABULARY, DAILY_PHRASES

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/topics")
async def get_topics():
    enriched = []
    for t in TOPICS:
        count = sum(1 for s in SUBTOPICS if s["topicId"] == t["id"])
        enriched.append({**t, "subtopicCount": count})
    return {"topics": enriched}


@router.get("/topics/{topic_id}")
async def get_topic(topic_id: str):
    topic = next((t for t in TOPICS if t["id"] == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    subtopics = [s for s in SUBTOPICS if s["topicId"] == topic_id]
    vocab = [v for v in VOCABULARY if v["topicId"] == topic_id]
    count = len(subtopics)
    return {**topic, "subtopicCount": count, "subtopics": subtopics, "vocabulary": vocab}


@router.get("/subtopics")
async def get_subtopics(topic_id: str | None = None):
    subs = SUBTOPICS
    if topic_id:
        subs = [s for s in subs if s["topicId"] == topic_id]
    return {"subtopics": subs}


@router.get("/subtopics/{subtopic_id}")
async def get_subtopic(subtopic_id: str):
    sub = next((s for s in SUBTOPICS if s["id"] == subtopic_id), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Subtopic not found")
    return sub


@router.get("/patterns")
async def get_patterns():
    return {"patterns": PATTERNS}


@router.get("/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    pattern = next((p for p in PATTERNS if p["id"] == pattern_id), None)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern


@router.get("/vocabulary")
async def get_vocabulary(topic_id: str | None = None):
    vocab = VOCABULARY
    if topic_id:
        vocab = [v for v in vocab if v["topicId"] == topic_id]
    return {"vocabulary": vocab}


@router.get("/daily-phrase")
async def get_daily_phrase():
    day_of_year = datetime.date.today().timetuple().tm_yday
    phrase = DAILY_PHRASES[day_of_year % len(DAILY_PHRASES)]
    return {"phrase": phrase, "date": str(datetime.date.today())}


@router.get("/daily-dialogue")
async def get_daily_dialogue():
    day_of_year = datetime.date.today().timetuple().tm_yday
    all_dialogues = [
        {"subtopicId": s["id"], "subtopicTitle": s["title"], **d}
        for s in SUBTOPICS
        for d in s["dialogues"]
    ]
    dialogue = all_dialogues[day_of_year % len(all_dialogues)]
    return {"dialogue": dialogue, "date": str(datetime.date.today())}
