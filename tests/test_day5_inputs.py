"""Day 5: bad input gives a clear error; slow tools time out."""
import time

import pytest

from jarvis.api import create_app
from jarvis.tools.registry import Registry, Tool, ToolError


def _reg(fn, timeout=1.0):
    reg = Registry(timeout=timeout)
    reg.register(Tool("t", "test", {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    }, fn))
    return reg


def test_missing_required_argument():
    assert _reg(lambda path: "ok").call("t", {}) == "error: missing required argument 'path'"


def test_unexpected_argument():
    out = _reg(lambda path: "ok").call("t", {"path": "a", "x": 1})
    assert out.startswith("error: unexpected argument 'x'")


@pytest.mark.parametrize("bad", [5, None, ["a"], True])
def test_wrong_type(bad):
    assert _reg(lambda path: "ok").call("t", {"path": bad}) == "error: argument 'path' must be of type string"


def test_slow_tool_times_out():
    def slow(path):
        time.sleep(1.5)
        return "late"
    start = time.time()
    out = _reg(slow, timeout=0.2).call("t", {"path": "a"})
    assert out == "error: tool timed out after 0.2s"
    assert time.time() - start < 1.0


def test_tool_error_and_crash_are_clear():
    def boom(path):
        raise ToolError("nope")
    def crash(path):
        raise RuntimeError("secret internals")
    assert _reg(boom).call("t", {"path": "a"}) == "error: nope"
    out = _reg(crash).call("t", {"path": "a"})
    assert out == "error: tool failed unexpectedly" and "secret" not in out


def test_read_note_empty_and_huge(cfg):
    from jarvis.tools.builtin import build_registry
    reg = build_registry(cfg)
    assert "required" in reg.call("read_note", {"path": ""})
    big = cfg.notes_dir / "big.md"
    big.write_text("x" * 50000)
    out = reg.call("read_note", {"path": "big.md"})
    assert "[truncated at 20000 characters]" in out and len(out) < 20100


@pytest.mark.parametrize("sid", ["a b", "../x", "x" * 65, ""])
def test_bad_session_id_rejected(cfg, sid):
    from conftest import FakeLLM, api_client
    client = api_client(create_app(cfg, FakeLLM([])), cfg)
    r = client.post("/chat", json={"message": "hi", "session_id": sid})
    assert r.status_code == 422
