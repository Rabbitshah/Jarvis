import json


from conftest import FakeLLM, api_client, text_chunk, tool_chunk
from jarvis.api import create_app


def parse(body):
    return [json.loads(l[6:]) for l in body.splitlines() if l.startswith("data: ")]


def test_health(cfg):
    r = api_client(create_app(cfg, FakeLLM([])), cfg).get("/health")
    assert r.status_code == 200 and "get_time" in r.json()["tools"]


def test_chat_streams_events(cfg):
    llm = FakeLLM([[tool_chunk("get_time", {})], [text_chunk("noon")]])
    r = api_client(create_app(cfg, llm), cfg).post("/chat", json={"message": "time?"})
    assert r.headers["content-type"].startswith("text/event-stream")
    kinds = [e["type"] for e in parse(r.text)]
    assert kinds == ["tool_call", "tool_result", "token", "done"]


def test_rejects_empty_message(cfg):
    r = api_client(create_app(cfg, FakeLLM([])), cfg).post("/chat", json={"message": ""})
    assert r.status_code == 422


def test_sessions_are_separate(cfg):
    llm = FakeLLM([[text_chunk("a")], [text_chunk("b")]])
    c = api_client(create_app(cfg, llm), cfg)
    c.post("/chat", json={"message": "x", "session_id": "s1"})
    c.post("/chat", json={"message": "y", "session_id": "s2"})
    assert [m["content"] for m in llm.calls[1] if m["role"] == "user"] == ["y"]
