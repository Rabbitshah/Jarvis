import dataclasses

import pytest

from jarvis.memory.ingest import ingest
from jarvis.memory.store import StoreError, VectorStore


class Counting:
    """Fake embedder that remembers how many texts it was asked to embed."""
    def __init__(self):
        self.texts = []

    def __call__(self, texts):
        self.texts.extend(texts)
        return [[float(t.lower().count(ch)) + 0.01 for ch in "abcd"] for t in texts]


@pytest.fixture
def c(cfg, tmp_path):
    (cfg.notes_dir / "bees.md").write_text("aaaa aaaa")
    (cfg.notes_dir / "dogs.md").write_text("dddd dddd")
    return dataclasses.replace(cfg, index_dir=tmp_path / "idx", ingest_exclude=())


def test_second_ingest_embeds_nothing(c):
    emb = Counting()
    first = ingest(c, emb)
    assert first.embedded == first.chunks == first.stored_total == 3   # idea.md, bees.md, dogs.md
    emb2 = Counting()
    second = ingest(c, emb2)
    assert emb2.texts == [] and second.embedded == 0
    assert sorted(second.unchanged) == ["bees.md", "dogs.md", "idea.md"]
    assert second.stored_total == second.chunks == 3


def test_only_the_changed_file_is_embedded(c):
    ingest(c, Counting())
    (c.notes_dir / "bees.md").write_text("aaaa aaaa and more bees")
    emb = Counting()
    res = ingest(c, emb)
    assert len(emb.texts) == 1 and "more bees" in emb.texts[0]
    assert sorted(res.unchanged) == ["dogs.md", "idea.md"] and res.stored_total == 3


def test_removed_and_new_files(c):
    ingest(c, Counting())
    (c.notes_dir / "dogs.md").unlink()
    (c.notes_dir / "cats.md").write_text("cccc")
    emb = Counting()
    res = ingest(c, emb)
    assert res.removed == ["dogs.md"] and len(emb.texts) == 1 and res.stored_total == 3
    with VectorStore(c.index_dir, None) as store:
        assert sorted(store.file_hashes()) == ["bees.md", "cats.md", "idea.md"]


@pytest.mark.parametrize("change", [
    {"memory_chunk_chars": 300}, {"memory_note_header": False}, {"memory_doc_prefix": "doc: "}, {"embed_model": "other"},
])
def test_changing_an_embedding_setting_reembeds_everything(c, change):
    ingest(c, Counting())
    emb = Counting()
    res = ingest(dataclasses.replace(c, **change), emb)
    assert res.embedded == 3 and res.unchanged == []


def test_full_flag_reembeds_everything(c):
    ingest(c, Counting())
    emb = Counting()
    assert ingest(c, emb, full=True).embedded == 3


def test_index_without_hashes_is_upgraded_once(c):
    ingest(c, Counting())
    with VectorStore(c.index_dir, None) as store:      # simulate an index made before hashes existed
        store.delete_file("bees.md")
        store.upsert([("bees.md", 0, "aaaa aaaa", [1.0, 0.0, 0.0, 0.0])])   # no hash given
    emb = Counting()
    res = ingest(c, emb)
    assert len(emb.texts) == 1 and res.unchanged == ["dogs.md", "idea.md"]
    assert ingest(c, Counting()).embedded == 0


def test_all_notes_deleted_empties_the_index(c):
    ingest(c, Counting())
    for f in c.notes_dir.iterdir():
        f.unlink()
    res = ingest(c, Counting())
    assert res.stored_total == 0 and sorted(res.removed) == ["bees.md", "dogs.md", "idea.md"]


def test_open_without_index_is_a_clear_error(tmp_path):
    with pytest.raises(StoreError, match="does not exist"):
        VectorStore(tmp_path / "nothing", None).__enter__()
