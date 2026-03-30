#!/usr/bin/env python3
"""One-time script: convert all Python data to JSON files. Run from backend/ folder."""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from data.content import TOPICS, SUBTOPICS, PATTERNS, VOCABULARY, DAILY_PHRASES

OUT = os.path.join(os.path.dirname(__file__), "..", "data-json")
SUB_DIR = os.path.join(OUT, "subtopics")
os.makedirs(SUB_DIR, exist_ok=True)

with open(os.path.join(OUT, "topics.json"), "w", encoding="utf-8") as f:
    json.dump(TOPICS, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "patterns.json"), "w", encoding="utf-8") as f:
    json.dump(PATTERNS, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "vocabulary.json"), "w", encoding="utf-8") as f:
    json.dump(VOCABULARY, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "daily-phrases.json"), "w", encoding="utf-8") as f:
    json.dump(DAILY_PHRASES, f, ensure_ascii=False, indent=2)

index = []
for sub in SUBTOPICS:
    sid = sub["id"]
    with open(os.path.join(SUB_DIR, f"{sid}.json"), "w", encoding="utf-8") as f:
        json.dump(sub, f, ensure_ascii=False, indent=2)
    index.append({
        "id": sid,
        "topicId": sub["topicId"],
        "title": sub["title"],
        "description": sub["description"],
        "dialogueCount": len(sub.get("dialogues", []))
    })

with open(os.path.join(SUB_DIR, "index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"Done: {len(SUBTOPICS)} subtopics, {len(TOPICS)} topics, {len(PATTERNS)} patterns, {len(VOCABULARY)} vocabulary, {len(DAILY_PHRASES)} phrases")
print(f"Output: {os.path.abspath(OUT)}")
