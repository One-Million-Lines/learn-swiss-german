"""Content discovery & dialogue resolution (published projections only)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.common.errors import not_found
from app.common.serialize import jsonable
from app.content.config_store import get_published_config
from app.db.client import get_db

SUPPORT_LANGUAGES = ("en", "es")


async def _published_item(kind: str, id_or_slug: str) -> Optional[dict]:
    db = get_db()
    query = {
        "kind": kind,
        "status": "published",
        "$or": [{"_id": id_or_slug}, {"slug": id_or_slug}, {"legacy_id": id_or_slug}],
    }
    return await db["content_items"].find_one(query)


async def _published_revision(item: dict) -> Optional[dict]:
    db = get_db()
    return await db["content_revisions"].find_one(
        {"item_id": item["_id"], "revision": item.get("published_revision", 1)}
    )


async def _load_utterances(ids: List[str]) -> Dict[str, dict]:
    ids = [i for i in ids if i]
    if not ids:
        return {}
    db = get_db()
    cursor = db["utterances"].find({"_id": {"$in": list(set(ids))}})
    return {u["_id"]: u async for u in cursor}


def _utext(utts: Dict[str, dict], uid: Optional[str]) -> Optional[str]:
    if not uid:
        return None
    u = utts.get(uid)
    return u.get("text") if u else None


async def resolve_dialogue(item: dict, support_language: str = "en") -> dict:
    """Resolve a dialogue item + revision into a language-aligned view."""
    revision = await _published_revision(item)
    if not revision:
        raise not_found("Dialogue revision not found.")
    payload = revision["payload"]

    # Collect all utterance IDs to batch-load.
    uids: List[str] = []
    for turn in payload.get("turns", []):
        uids += [turn.get("utterance_id"), turn.get("german_utterance_id")]
        uids += list((turn.get("translation_utterance_ids") or {}).values())
    for kp in payload.get("key_phrases", []):
        uids += [kp.get("swiss_utterance_id"), kp.get("german_utterance_id")]
        uids += list((kp.get("translation_utterance_ids") or {}).values())
    for diff in payload.get("comparison_notes", []):
        uids += [diff.get("swiss_utterance_id"), diff.get("german_utterance_id")]
    utts = await _load_utterances(uids)

    def tr(mapping: dict) -> Optional[str]:
        ids = mapping or {}
        return _utext(utts, ids.get(support_language)) or _utext(utts, ids.get("en"))

    def tr_all(mapping: dict) -> dict:
        ids = mapping or {}
        return {lang: _utext(utts, uid) for lang, uid in ids.items() if _utext(utts, uid)}

    turns = []
    for turn in payload.get("turns", []):
        turns.append({
            "id": turn.get("id"),
            "speaker": turn.get("speaker"),
            "speaker_id": turn.get("speaker_id"),
            "swiss_german": _utext(utts, turn.get("utterance_id")),
            "german": _utext(utts, turn.get("german_utterance_id")),
            "translation": tr(turn.get("translation_utterance_ids")),
            "translations": tr_all(turn.get("translation_utterance_ids")),
            "utterance_id": turn.get("utterance_id"),
            "objective_ids": turn.get("objective_ids", []),
        })

    differences = [
        {
            "swiss_german": _utext(utts, d.get("swiss_utterance_id")),
            "german": _utext(utts, d.get("german_utterance_id")),
            "explanation": d.get("explanation"),
        }
        for d in payload.get("comparison_notes", [])
    ]
    key_phrases = [
        {
            "swiss_german": _utext(utts, kp.get("swiss_utterance_id")),
            "german": _utext(utts, kp.get("german_utterance_id")),
            "translation": tr(kp.get("translation_utterance_ids")),
            "translations": tr_all(kp.get("translation_utterance_ids")),
        }
        for kp in payload.get("key_phrases", [])
    ]

    return {
        "id": item["_id"],
        "slug": item.get("slug"),
        "legacy_id": item.get("legacy_id"),
        "revision": revision["revision"],
        "title": payload.get("title"),
        "situation": payload.get("situation"),
        "level": payload.get("level"),
        "register": payload.get("register"),
        "dialect_id": item.get("dialect_id"),
        "dialect_verified": payload.get("dialect_verified", False),
        "dialect_label": payload.get("dialect_label"),
        "subtopic_id": item.get("subtopic_id"),
        "topic_id": item.get("topic_id"),
        "support_language": support_language,
        "turns": turns,
        "differences": differences,
        "key_phrases": key_phrases,
    }


async def get_dialogue(id_or_slug: str, support_language: str = "en") -> dict:
    item = await _published_item("dialogue", id_or_slug)
    if not item:
        raise not_found("Dialogue not found.")
    return await resolve_dialogue(item, support_language)


async def list_topics() -> List[dict]:
    db = get_db()
    cursor = db["content_items"].find({"kind": "topic", "status": "published"}).sort("sort_order", 1)
    topics = [t async for t in cursor]
    out = []
    for t in topics:
        count = await db["content_items"].count_documents(
            {"kind": "subtopic", "status": "published", "topic_id": t["slug"]}
        )
        disc = t.get("discovery", {})
        out.append({
            "id": t["slug"], "title": disc.get("title"), "description": disc.get("description"),
            "icon": disc.get("icon"), "color": disc.get("color"), "subtopic_count": count,
        })
    return out


async def get_topic(id_or_slug: str) -> dict:
    db = get_db()
    item = await _published_item("topic", id_or_slug)
    if not item:
        raise not_found("Topic not found.")
    disc = item.get("discovery", {})
    sub_cursor = db["content_items"].find(
        {"kind": "subtopic", "status": "published", "topic_id": item["slug"]}
    ).sort("sort_order", 1)
    subtopics = []
    async for s in sub_cursor:
        sdisc = s.get("discovery", {})
        subtopics.append({
            "id": s["slug"], "title": sdisc.get("title"), "description": sdisc.get("description"),
            "dialogue_count": sdisc.get("dialogue_count", 0),
        })
    vocab_cursor = db["content_items"].find(
        {"kind": "vocabulary_group", "status": "published", "topic_id": item["slug"]}
    ).sort("sort_order", 1)
    vocabulary = [await _vocab_view(v) async for v in vocab_cursor]
    return {
        "id": item["slug"], "title": disc.get("title"), "description": disc.get("description"),
        "icon": disc.get("icon"), "color": disc.get("color"),
        "subtopic_count": len(subtopics), "subtopics": subtopics, "vocabulary": vocabulary,
    }


async def get_subtopic(id_or_slug: str, support_language: str = "en") -> dict:
    item = await _published_item("subtopic", id_or_slug)
    if not item:
        raise not_found("Subtopic not found.")
    revision = await _published_revision(item)
    payload = revision["payload"] if revision else {}
    dialogues = []
    db = get_db()
    for dialogue_item_id in payload.get("dialogue_item_ids", []):
        ditem = await db["content_items"].find_one({"_id": dialogue_item_id, "status": "published"})
        if ditem:
            dialogues.append(await resolve_dialogue(ditem, support_language))
    return {
        "id": item["slug"], "topic_id": item.get("topic_id"),
        "title": payload.get("title"), "description": payload.get("description"),
        "dialogues": dialogues,
    }


async def _vocab_view(item: dict) -> dict:
    revision = await _published_revision(item)
    payload = revision["payload"] if revision else {}
    uids: List[str] = []
    for w in payload.get("words", []):
        uids += [w.get("swiss_utterance_id"), w.get("german_utterance_id")]
        uids += list((w.get("translation_utterance_ids") or {}).values())
    utts = await _load_utterances(uids)
    words = [
        {
            "swiss_german": _utext(utts, w.get("swiss_utterance_id")),
            "german": _utext(utts, w.get("german_utterance_id")),
            "english": _utext(utts, (w.get("translation_utterance_ids") or {}).get("en")),
            "spanish": _utext(utts, (w.get("translation_utterance_ids") or {}).get("es")),
        }
        for w in payload.get("words", [])
    ]
    return {"id": item["slug"], "topic_id": item.get("topic_id"),
            "title": payload.get("title"), "words": words}


async def list_vocabulary(topic_id: Optional[str] = None) -> List[dict]:
    db = get_db()
    query = {"kind": "vocabulary_group", "status": "published"}
    if topic_id:
        query["topic_id"] = topic_id
    cursor = db["content_items"].find(query).sort("sort_order", 1)
    return [await _vocab_view(v) async for v in cursor]


async def list_patterns() -> List[dict]:
    db = get_db()
    cursor = db["content_items"].find({"kind": "pattern", "status": "published"}).sort("sort_order", 1)
    out = []
    async for item in cursor:
        revision = await _published_revision(item)
        payload = revision["payload"] if revision else {}
        uids: List[str] = []
        for ex in payload.get("examples", []):
            uids += [ex.get("swiss_utterance_id"), ex.get("german_utterance_id")]
            uids += list((ex.get("translation_utterance_ids") or {}).values())
        utts = await _load_utterances(uids)
        examples = [
            {
                "swiss_german": _utext(utts, ex.get("swiss_utterance_id")),
                "german": _utext(utts, ex.get("german_utterance_id")),
                "english": _utext(utts, (ex.get("translation_utterance_ids") or {}).get("en")),
                "spanish": _utext(utts, (ex.get("translation_utterance_ids") or {}).get("es")),
            }
            for ex in payload.get("examples", [])
        ]
        out.append({"id": item["slug"], "title": payload.get("title"),
                    "description": payload.get("description"), "examples": examples})
    return out


async def search(q: str, kind: Optional[str] = None, limit: int = 20) -> List[dict]:
    db = get_db()
    if not q or len(q.strip()) < 2:
        return []
    query: dict = {"status": "published", "search_text": {"$regex": _escape(q.strip().lower())}}
    if kind:
        query["kind"] = kind
    cursor = db["content_items"].find(
        query, {"slug": 1, "kind": 1, "discovery": 1, "topic_id": 1, "title": 1}
    ).limit(min(limit, 100))
    return [
        {"id": d["slug"], "kind": d["kind"], "title": (d.get("discovery") or {}).get("title") or d.get("title"),
         "topic_id": d.get("topic_id")}
        async for d in cursor
    ]


def _escape(text: str) -> str:
    import re
    return re.escape(text)


async def daily_selection(support_language: str = "en") -> dict:
    """Deterministic daily phrase + dialogue for the editorial date (Europe/Zurich)."""
    from app.common.timeutil import editorial_date

    db = get_db()
    date_str = editorial_date("Europe/Zurich")
    seed = int(date_str.replace("-", ""))

    # Deterministic dialogue pick from published dialogues.
    dialogue_ids = [
        d["_id"] async for d in db["content_items"]
        .find({"kind": "dialogue", "status": "published"}, {"_id": 1})
        .sort("_id", 1)
    ]
    daily_dialogue = None
    if dialogue_ids:
        chosen = dialogue_ids[seed % len(dialogue_ids)]
        item = await db["content_items"].find_one({"_id": chosen})
        daily_dialogue = await resolve_dialogue(item, support_language)

    # Deterministic phrase from key phrases of a published dialogue (first turn).
    daily_phrase = None
    if daily_dialogue and daily_dialogue["turns"]:
        turn = daily_dialogue["turns"][seed % len(daily_dialogue["turns"])]
        daily_phrase = {
            "swiss_german": turn["swiss_german"], "german": turn["german"],
            "translation": turn["translation"], "topic": daily_dialogue.get("title"),
        }
    return {"date": date_str, "phrase": daily_phrase, "dialogue": daily_dialogue}


async def home(support_language: str = "en", dialect_id: Optional[str] = None) -> dict:
    homepage = await get_published_config("homepage") or {}
    topics = await list_topics()
    daily = await daily_selection(support_language)
    # Sample dialogue: first 4 turns of the daily dialogue.
    sample = None
    if daily.get("dialogue"):
        d = daily["dialogue"]
        sample = {**d, "turns": d["turns"][:4]}
    creators = await featured_creators()
    return {
        "homepage": jsonable(homepage),
        "topics": topics,
        "daily": daily,
        "sample": sample,
        "creators": creators,
    }


async def featured_creators(limit: int = 3) -> List[dict]:
    db = get_db()
    cursor = db["creators"].find(
        {"status": "published", "featured_order": {"$ne": None}}
    ).sort("featured_order", 1).limit(limit)
    out = []
    async for c in cursor:
        out.append({
            "slug": c["slug"], "name": c["name"], "bio": c.get("bio"),
            "dialect_ids": c.get("dialect_ids", []), "topic_ids": c.get("topic_ids", []),
            "profile_links": c.get("profile_links", []),
            "attribution": c.get("attribution"),
        })
    return out


async def list_dialects(include_coming_soon: bool = True) -> List[dict]:
    db = get_db()
    statuses = ["enabled", "coming_soon"] if include_coming_soon else ["enabled"]
    cursor = db["dialects"].find({"status": {"$in": statuses}}).sort("sort_order", 1)
    return [
        {"code": d["code"], "labels": d.get("labels"), "description": d.get("description"),
         "regional_variety": d.get("regional_variety"), "language_tag": d.get("language_tag"),
         "status": d.get("status"), "voice_review_status": d.get("voice_review_status")}
        async for d in cursor
    ]
