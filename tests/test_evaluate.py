import dataclasses

from jarvis.memory.evaluate import load_cases, run_cases, summarize
from jarvis.memory.ingest import embed_text, ingest


def fake_embed(texts):
    return [[float(t.lower().count(ch)) + 0.01 for ch in "abcd"] for t in texts]


def test_scores_and_any_of_notes(cfg, tmp_path):
    (cfg.notes_dir / "bees.md").write_text("aaaa aaaa aaaa")
    (cfg.notes_dir / "dogs.md").write_text("dddd dddd dddd")
    c = dataclasses.replace(cfg, index_dir=tmp_path / "idx", ingest_exclude=())
    ingest(c, fake_embed)
    cases = [
        {"question": "aaa", "note": "bees.md"},
        {"question": "ddd", "note": ["nope.md", "dogs.md"]},   # any of them counts
        {"question": "aaa", "note": "nowhere.md"},              # a miss
    ]
    s = summarize(run_cases(c, fake_embed, cases))
    assert (s.n, s.top1, s.hit3, s.hit5) == (3, 2, 2, 2)
    assert abs(s.mrr - 2 / 3) < 1e-9


def test_load_cases(tmp_path):
    f = tmp_path / "c.toml"
    f.write_text('[[case]]\nquestion="q"\nnote="a.md"\n[offtopic]\nquestions=["x"]\n')
    cases, off = load_cases(f)
    assert cases == [{"question": "q", "note": "a.md"}] and off == ["x"]


def test_prefixes_and_header_are_applied(cfg, tmp_path):
    assert embed_text("a/b.md", "hi", header=False, prefix="P: ") == "P: hi"
    seen = []
    (cfg.notes_dir / "bees.md").write_text("aaaa")
    c = dataclasses.replace(cfg, index_dir=tmp_path / "idx", ingest_exclude=(), memory_doc_prefix="DOC: ",
                            memory_query_prefix="Q: ", memory_note_header=False)
    ingest(c, lambda t: seen.extend(t) or fake_embed(t))
    assert all(t.startswith("DOC: ") and "Note:" not in t for t in seen)
    from jarvis.memory.search import search_notes
    seen.clear()
    search_notes(c, lambda t: seen.extend(t) or fake_embed(t), "hello")
    assert seen == ["Q: hello"]
