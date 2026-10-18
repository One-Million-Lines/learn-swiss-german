"""Migration determinism and reconciliation (DATA-01, DATA-02)."""
import os

from app.content.migrate import build_documents

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data-json"))


def test_source_counts_match_baseline():
    _, counts = build_documents(DATA_DIR)
    assert counts["topics"] == 9
    assert counts["subtopics"] == 120
    assert counts["dialogues"] == 606
    assert counts["turns"] == 4891


def test_migration_is_deterministic():
    docs1, _ = build_documents(DATA_DIR)
    docs2, _ = build_documents(DATA_DIR)
    ids1 = {c: sorted(d["_id"] for d in v) for c, v in docs1.items()}
    ids2 = {c: sorted(d["_id"] for d in v) for c, v in docs2.items()}
    assert ids1 == ids2


async def test_persisted_content_present(db):
    items = await db["content_items"].count_documents({"status": "published"})
    assert items >= 770
    # Legacy Swiss utterances are dialect-unverified (never auto-labelled Zurich).
    sample = await db["utterances"].find_one({"language_tag": "gsw-CH"})
    assert sample["dialect_id"] is None
