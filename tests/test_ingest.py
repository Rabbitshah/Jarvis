import dataclasses

import pytest

from jarvis.memory.chunker import chunk_text
from jarvis.memory.ingest import embed_text, ingest
from jarvis.memory.store import VectorStore


def fake_embed(texts):
    # tiny deterministic "embedding": which of 4 letters the text has most of
    return [[float(t.lower().count(ch)) + 0.01 for ch in "abcd"] for t in texts]


def test_short_note_is_one_chunk():
    assert chunk_text("# Title\n\nShort note.") == ["# Title\n\nShort note."]


def test_chunks_respect_limit_and_lose_nothing():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 40 for i in range(12))
    chunks = chunk_text(text, 400)
    assert len(chunks) > 1 and all(len(c) <= 400 for c in chunks)
    joined = " ".join(chunks)
    assert all(f"Paragraph {i}." in joined for i in range(12))


def test_one_huge_paragraph_is_cut():
    chunks = chunk_text("x" * 2500, 800)
    assert [len(c) for c in chunks] == [800, 800, 800, 100]


def test_heading_stays_with_its_text():
    text = "a" * 60 + "\n\n" + "## Heading\n\n" + "b" * 60
    chunks = chunk_text(text, 70)
    assert any(c.startswith("## Heading") and "bbb" in c for c in chunks)


def test_empty_and_bad_limit():
    assert chunk_text("  \n\n ") == []
    with pytest.raises(ValueError):
        chunk_text("x", 10)


def _cfg(cfg, tmp_path):
    return dataclasses.replace(cfg, index_dir=tmp_path / "idx", ingest_exclude=("README.md", "sample-*"))


def test_ingest_count_matches_and_skips(cfg, tmp_path):
    (cfg.notes_dir / "README.md").write_text("how to use")
    (cfg.notes_dir / "sample-x.md").write_text("demo")
    (cfg.notes_dir / "long.md").write_text("\n\n".join("para %d " % i + "q" * 300 for i in range(5)))
    c = _cfg(cfg, tmp_path)
    res = ingest(c, fake_embed, max_chars=700)
    assert sorted(res.skipped) == ["README.md", "sample-x.md"]
    assert set(res.files) == {"idea.md", "long.md"}
    assert res.files["idea.md"] == 1 and res.files["long.md"] > 1
    assert res.stored_total == res.chunks


def test_reingest_does_not_duplicate_and_drops_stale(cfg, tmp_path):
    c = _cfg(cfg, tmp_path)
    note = cfg.notes_dir / "long.md"
    note.write_text("\n\n".join("para %d " % i + "q" * 300 for i in range(6)))
    first = ingest(c, fake_embed, max_chars=700)
    note.write_text("now short")
    second = ingest(c, fake_embed, max_chars=700)
    assert second.files["long.md"] == 1
    assert second.stored_total == second.chunks < first.chunks


def test_search_finds_right_note(cfg, tmp_path):
    (cfg.notes_dir / "bees.md").write_text("aaaa aaaa aaaa")
    (cfg.notes_dir / "dogs.md").write_text("dddd dddd dddd")
    c = _cfg(cfg, tmp_path)
    ingest(c, fake_embed)
    with VectorStore(c.index_dir, 4) as store:
        hit = store.search(fake_embed(["note: bees aaaa"])[0], k=1)[0]
    assert hit.file == "bees.md"


def test_embed_text_has_file_name():
    assert embed_text("folder/08-jarvis.md", "hi").startswith("Note: 08-jarvis")


def test_nothing_to_ingest(cfg, tmp_path):
    for f in cfg.notes_dir.iterdir():
        f.unlink()
    res = ingest(_cfg(cfg, tmp_path), fake_embed)
    assert res.chunks == 0 and res.stored_total == 0


def test_memory_file_is_indexed_without_its_header():
    from jarvis.memory.ingest import indexable_text
    text = "# Memory\n\nFacts Jarvis was asked to remember. One per line.\n\n- 2026-10-25: You play pickleball on weekends\n- 2026-10-26: You like green tea\n"
    assert indexable_text("memory.md", text) == "You play pickleball on weekends\n\nYou like green tea"
    assert indexable_text("other.md", text) == text
    assert indexable_text("memory.md", "# Memory\n\nnothing yet\n") == ""
