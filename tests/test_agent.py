from conftest import FakeLLM, text_chunk, tool_chunk
from jarvis.agent import Agent
from jarvis.llm import LLMError
from jarvis.tools.builtin import build_registry


def make(cfg, rounds, **kw):
    return Agent(FakeLLM(rounds), build_registry(cfg), "sys", **kw)


def test_plain_answer(cfg):
    agent = make(cfg, [[text_chunk("Hel"), text_chunk("lo")]])
    events = list(agent.chat("hi"))
    assert "".join(e["text"] for e in events if e["type"] == "token") == "Hello"
    assert events[-1] == {"type": "done"}


def test_tool_round_trip(cfg):
    agent = make(cfg, [[tool_chunk("read_note", {"path": "idea.md"})], [text_chunk("Done")]])
    events = list(agent.chat("what is in idea.md"))
    kinds = [e["type"] for e in events]
    assert kinds == ["tool_call", "tool_result", "token", "done"]
    assert "December" in events[1]["result"]
    assert agent.messages[-3]["role"] == "assistant" and agent.messages[-3]["tool_calls"]
    assert agent.messages[-2]["role"] == "tool"


def test_tool_error_goes_back_to_model(cfg):
    agent = make(cfg, [[tool_chunk("read_note", {"path": "../x.md"})], [text_chunk("sorry")]])
    result = [e for e in agent.chat("go") if e["type"] == "tool_result"][0]["result"]
    assert result.startswith("error:")


def test_loop_limit(cfg):
    rounds = [[tool_chunk("get_time", {})] for _ in range(3)]
    events = list(make(cfg, rounds, max_rounds=3).chat("loop"))
    assert events[-1]["type"] == "error" and "limit" in events[-1]["message"]


def test_llm_error_becomes_event(cfg):
    class Boom:
        def chat_stream(self, *a, **k):
            raise LLMError("down")
            yield  # pragma: no cover

    events = list(Agent(Boom(), build_registry(cfg), "sys").chat("hi"))
    assert events == [{"type": "error", "message": "down"}]


def test_history_remembered_and_trimmed(cfg):
    agent = make(cfg, [[text_chunk("a")], [text_chunk("b")]], max_history=4)
    list(agent.chat("one"))
    list(agent.chat("two"))
    assert agent.messages[0]["role"] == "system"
    assert agent.messages[1]["role"] == "user"
    assert len(agent.messages) <= 5


def test_reset(cfg):
    agent = make(cfg, [[text_chunk("a")]])
    list(agent.chat("one"))
    agent.reset()
    assert len(agent.messages) == 1


def test_tool_call_written_as_text_is_rescued(cfg):
    agent = make(cfg, [[text_chunk('{"name": "get_time", '), text_chunk('"parameters": {}}')], [text_chunk("noon")]])
    events = list(agent.chat("time?"))
    assert [e["type"] for e in events] == ["tool_call", "tool_result", "token", "done"]
    assert events[2]["text"] == "noon"


def test_json_that_is_not_a_tool_is_shown(cfg):
    agent = make(cfg, [[text_chunk('{"hello": 1}')]])
    events = list(agent.chat("json please"))
    assert events[0] == {"type": "token", "text": '{"hello": 1}'}
    assert events[-1] == {"type": "done"}
