import dataclasses

from conftest import FakeLLM, text_chunk
from jarvis.agent import Agent
from jarvis.memory.context import HEADER, build_context, make_context_fn
from jarvis.memory.ingest import ingest
from jarvis.memory.store import Hit
from jarvis.tools.builtin import build_registry


def fake_embed(texts):
    return [[float(t.lower().count(ch)) + 0.01 for ch in "abcd"] for t in texts]


def _agent(cfg, llm, ctx_fn):
    return Agent(llm, build_registry(cfg), "sys", 4, 40, ctx_fn)


def test_build_context_has_files_header_and_data_framing():
    ctx = build_context([Hit("a.md", 0, "alpha", 0.9), Hit("a.md", 1, "more", 0.8), Hit("b.md", 0, "beta", 0.7)])
    assert ctx.files == ["a.md", "b.md"]
    assert HEADER in ctx.text and "[a.md]\nalpha" in ctx.text and "<notes>" in ctx.text
    assert build_context([]) is None


def test_excerpts_reach_the_model_but_not_the_history(cfg):
    llm = FakeLLM([[text_chunk("ok")]])
    ctx = build_context([Hit("idea.md", 0, "Ship by December", 0.9)])
    agent = _agent(cfg, llm, lambda q: ctx)
    events = list(agent.chat("when do I ship?"))
    sent = llm.calls[0][-1]["content"]
    assert "Ship by December" in sent and sent.endswith("Question: when do I ship?")
    assert agent.messages[1] == {"role": "user", "content": "when do I ship?"}  # plain in history
    assert events[0] == {"type": "sources", "files": ["idea.md"]}
    assert events[-1]["type"] == "done"


def test_no_context_means_plain_question(cfg):
    llm = FakeLLM([[text_chunk("hi")]])
    events = list(_agent(cfg, llm, lambda q: None).chat("hello"))
    assert llm.calls[0][-1]["content"] == "hello"
    assert all(e["type"] != "sources" for e in events)


def test_context_fn_works_with_real_search_and_threshold(cfg, tmp_path):
    (cfg.notes_dir / "bees.md").write_text("aaaa aaaa aaaa")
    c = dataclasses.replace(cfg, index_dir=tmp_path / "idx", ingest_exclude=(), memory_min_score=0.0)
    ingest(c, fake_embed)
    ctx = make_context_fn(c, fake_embed)("aaa")
    assert ctx and "bees.md" in ctx.files
    strict = dataclasses.replace(c, memory_min_score=1.1)  # nothing can reach this score
    assert make_context_fn(strict, fake_embed)("aaa") is None


def test_broken_index_never_breaks_chat(cfg, tmp_path):
    c = dataclasses.replace(cfg, index_dir=tmp_path / "missing")
    assert make_context_fn(c, fake_embed)("anything") is None
    off = dataclasses.replace(cfg, memory_enabled=False)
    assert make_context_fn(off, fake_embed)("anything") is None
