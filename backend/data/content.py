"""
All content loaded from JSON files in ../data-json/
Drop a new .json file in data-json/subtopics/ and it's auto-discovered.
"""
import json, glob, os

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data-json")

def _load(filename):
    with open(os.path.join(_DATA_DIR, filename), encoding="utf-8") as f:
        return json.load(f)

def _load_subtopics():
    files = sorted(glob.glob(os.path.join(_DATA_DIR, "subtopics", "*.json")))
    return [json.load(open(f, encoding="utf-8")) for f in files if not f.endswith("index.json")]

TOPICS = _load("topics.json")
PATTERNS = _load("patterns.json")
VOCABULARY = _load("vocabulary.json")
DAILY_PHRASES = _load("daily-phrases.json")
SUBTOPICS = _load_subtopics()
