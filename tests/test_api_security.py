"""Host and Origin checks (DNS rebinding, cross-site POSTs). No auth is tested because there is none."""
import dataclasses
import json

import pytest

from conftest import FakeLLM, api_client, text_chunk
from jarvis.api import create_app
from jarvis.config import load_config
from jarvis.memory.remember import MEMORY_FILE

NOOP = {"session_id": "none", "id": "x", "approve": True}
BODY = {"message": "remember that I like green tea", "session_id": "s"}


def make(cfg, **kw):
    return api_client(create_app(dataclasses.replace(cfg, **kw), FakeLLM([])), cfg)


def test_allowed_hosts_pass(cfg):
    c = make(cfg)
    for host in ("127.0.0.1", "localhost", "[::1]"):
        assert c.get("/health", headers={"Host": f"{host}:{cfg.api_port}"}).status_code == 200


@pytest.mark.parametrize("host", ["evil.example", "evil.example:8000", "127.0.0.1", "127.0.0.1:9999", "localhost.evil.example:8000"])
def test_bad_host_is_403_even_for_health(cfg, host):
    r = make(cfg).get("/health", headers={"Host": host})
    assert r.status_code == 403 and r.json() == {"error": "host not allowed"}


def test_rebinding_style_post_does_not_reach_the_agent(cfg):
    r = make(cfg).post("/chat", json=BODY, headers={"Host": "evil.example:8000"})
    assert r.status_code == 403 and not (cfg.notes_dir / MEMORY_FILE).exists()


@pytest.mark.parametrize("path,body", [("/chat", BODY), ("/confirm", {"session_id": "s", "id": "x", "approve": True}),
                                        ("/forget", {"session_id": "s"})])
def test_bad_origin_post_is_403_and_writes_nothing(cfg, path, body):
    r = make(cfg).post(path, json=body, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403 and r.json() == {"error": "origin not allowed"}
    assert not (cfg.notes_dir / MEMORY_FILE).exists()


def test_origin_null_is_refused(cfg):
    assert make(cfg).post("/chat", json=BODY, headers={"Origin": "null"}).status_code == 403


def test_good_and_missing_origin_pass(cfg):
    c = make(cfg)
    for origin in (f"http://127.0.0.1:{cfg.api_port}", f"http://localhost:{cfg.api_port}", f"http://[::1]:{cfg.api_port}/", None):
        headers = {"Origin": origin} if origin else {}
        assert c.post("/confirm", json=NOOP, headers=headers).status_code == 404  # reaches the app: unknown session


def test_get_ignores_origin(cfg):
    assert make(cfg).get("/health", headers={"Origin": "https://evil.example"}).status_code == 200


def test_extra_origin_from_config_and_its_host_pass(cfg):
    c = make(cfg, api_allowed_origins=("http://127.0.0.1:5173",))
    r = c.post("/confirm", json=NOOP, headers={"Origin": "http://127.0.0.1:5173", "Host": "127.0.0.1:5173"})
    assert r.status_code == 404


def test_extra_origin_from_env(cfg, monkeypatch):
    monkeypatch.setenv("JARVIS_ALLOWED_ORIGINS", "http://127.0.0.1:5173, http://localhost:5173")
    loaded = load_config()
    assert loaded.api_allowed_origins == ("http://127.0.0.1:5173", "http://localhost:5173")
    r = make(cfg, api_allowed_origins=loaded.api_allowed_origins).post(
        "/confirm", json=NOOP, headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 404


def test_text_plain_post_is_rejected_by_the_body_parser(cfg):
    r = make(cfg).post("/chat", content=json.dumps(BODY), headers={"Content-Type": "text/plain"})
    assert r.status_code == 422 and not (cfg.notes_dir / MEMORY_FILE).exists()


def test_streaming_still_streams(cfg):
    llm = FakeLLM([[text_chunk("a")]])
    r = api_client(create_app(cfg, llm), cfg).post("/chat", json={"message": "hi"})
    assert r.headers["content-type"].startswith("text/event-stream") and '"done"' in r.text
