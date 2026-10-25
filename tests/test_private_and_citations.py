import dataclasses

import pytest

from conftest import FakeLLM, text_chunk, tool_chunk
from jarvis.agent import Agent
from jarvis.memory.ingest import ingest
from jarvis.memory.search import search_notes
from jarvis.tools.builtin import build_registry
from jarvis.tools.notes import is_private

PRIVATE = ("private/*", "*password*", "*salary*")


def fake_embed(texts):
    return [[float(t.lower().count(ch)) + 0.01 for ch in "abcd"] for t in texts]


@pytest.fixture
def p(cfg, tmp_path):
    (cfg.notes_dir / "private").mkdir()
    (cfg.notes_dir / "private" / "bank.md").write_text("aaaa account number")
    (cfg.notes_dir / "my-Salary-2026.md").write_text("aaaa pay details")
    (cfg.notes_dir / "bees.md").write_text("aaaa bees")
    return dataclasses.replace(cfg, index_dir=tmp_path / "idx", ingest_exclude=(), private_notes=PRIVATE, memory_min_score=0.0)


def test_pattern_matching():
    assert is_private("private/bank.md", PRIVATE) and is_private("My-Salary-2026.md", PRIVATE)
    assert is_private("work/Passwords.txt", PRIVATE)
    assert not is_private("bees.md", PRIVATE) and not is_private("privateer.md", PRIVATE)


def test_private_notes_are_invisible_to_the_tools(p):
    reg = build_registry(p, fake_embed)
    listing = reg.call("list_notes", {})
    assert "bees.md" in listing and "bank" not in listing and "alary" not in listing
    missing = reg.call("read_note", {"path": "does-not-exist.md"})
    assert reg.call("read_note", {"path": "private/bank.md"}) == missing        # same answer as a missing note
    assert reg.call("read_note", {"path": "bank"}) != "aaaa account number"      # plain-name lookup cannot find it
    assert "aaaa" not in reg.call("read_note", {"path": "my-Salary-2026.md"})
    assert "aaaa" not in reg.call("read_note", {"path": "PRIVATE/bank.md"})      # case tricks do not help


def test_private_notes_are_never_indexed_and_old_chunks_are_pruned(p):
    open_cfg = dataclasses.replace(p, private_notes=())
    ingest(open_cfg, fake_embed)                       # earlier, before the rule existed: everything indexed
    assert {h.file for h in search_notes(open_cfg, fake_embed, "aaaa", k=10)} >= {"private/bank.md", "my-Salary-2026.md"}
    res = ingest(p, fake_embed)                        # rule now active
    assert sorted(res.removed) == ["my-Salary-2026.md", "private/bank.md"]
    assert {h.file for h in search_notes(p, fake_embed, "aaaa", k=10)} == {"bees.md", "idea.md"}


def test_search_drops_stale_private_hits_even_before_reingest(p):
    ingest(dataclasses.replace(p, private_notes=()), fake_embed)
    files = {h.file for h in search_notes(p, fake_embed, "aaaa", k=10)}
    assert "private/bank.md" not in files and "my-Salary-2026.md" not in files


def test_sources_come_from_code_not_the_model(p):
    ingest(p, fake_embed)
    from jarvis.memory.context import make_context_fn
    llm = FakeLLM([[text_chunk("Bees are in a note. (source: totally-wrong.md)")]])
    agent = Agent(llm, build_registry(p, fake_embed), "sys", 4, 40, make_context_fn(p, fake_embed))
    events = list(agent.chat("tell me about aaaa bees"))
    src = [e for e in events if e["type"] == "sources"]
    assert len(src) == 1 and "bees.md" in src[0]["files"] and "totally-wrong.md" not in src[0]["files"]


def test_search_notes_tool_results_are_cited(p):
    ingest(p, fake_embed)
    llm = FakeLLM([[tool_chunk("search_notes", {"query": "aaaa bees"})], [text_chunk("ok")]])
    agent = Agent(llm, build_registry(p, fake_embed), "sys", 4, 40, None)
    events = list(agent.chat("what do my notes say about bees"))
    assert [e for e in events if e["type"] == "sources"][0]["files"][0] == "bees.md"


def test_no_sources_when_no_notes_were_used(cfg):
    llm = FakeLLM([[text_chunk("It is noon.")]])
    events = list(Agent(llm, build_registry(cfg, fake_embed), "sys", 4, 40, None).chat("what time is it"))
    assert all(e["type"] != "sources" for e in events)
