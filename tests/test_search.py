import dataclasses

import pytest

from jarvis.memory.ingest import ingest
from jarvis.memory.search import search_notes
from jarvis.memory.store import StoreError


def fake_embed(texts):
    return [[float(t.lower().count(ch)) + 0.01 for ch in "abcd"] for t in texts]


@pytest.fixture
def indexed(cfg, tmp_path):
    (cfg.notes_dir / "bees.md").write_text("aaaa aaaa aaaa")
    (cfg.notes_dir / "dogs.md").write_text("dddd dddd dddd")
    c = dataclasses.replace(cfg, index_dir=tmp_path / "idx", ingest_exclude=())
    ingest(c, fake_embed)
    return c


def test_finds_right_note_and_respects_k(indexed):
    hits = search_notes(indexed, fake_embed, "aaa", k=2)
    assert hits[0].file == "bees.md" and len(hits) == 2
    assert len(search_notes(indexed, fake_embed, "aaa", k=99)) <= 10  # k is capped, no crash


@pytest.mark.parametrize("q", ["", "   ", "x" * 501])
def test_bad_query_is_a_clear_error(indexed, q):
    with pytest.raises(StoreError):
        search_notes(indexed, fake_embed, q)


def test_missing_index_is_clear_and_creates_nothing(cfg, tmp_path):
    c = dataclasses.replace(cfg, index_dir=tmp_path / "nope")
    with pytest.raises(StoreError, match="ingest"):
        search_notes(c, fake_embed, "hello")
    assert not (tmp_path / "nope").exists()
