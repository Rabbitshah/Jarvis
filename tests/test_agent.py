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


def test_answer_wrapped_in_json_is_unwrapped(cfg):
    for raw, want in [('{"output": "It is 11:35 AM."}', "It is 11:35 AM."),
                      ('{"return": "datetime", "value": "11:33"}', "11:33")]:
        agent = make(cfg, [[text_chunk(raw)]])
        events = list(agent.chat("time?"))
        assert events[0] == {"type": "token", "text": want}
        assert agent.messages[-1]["content"] == want  # history is clean too


def test_other_json_is_left_alone(cfg):
    for raw in ['{"a": 1, "output": "x"}', '{"output": 5}', '{"x": "y"}', '{"output": "a", "b": "c", "d": "e"}']:
        agent = make(cfg, [[text_chunk(raw)]])
        assert list(agent.chat("json"))[0]["text"] == raw


def test_answer_round_after_a_tool_gets_no_tools(cfg):
    agent = make(cfg, [[tool_chunk("get_time", {})], [text_chunk("noon")]])
    list(agent.chat("time?"))
    assert agent.llm.tools_offered == [True, False]


def test_tools_stay_on_after_list_notes_or_an_error(cfg):
    agent = make(cfg, [[tool_chunk("list_notes", {})], [tool_chunk("read_note", {"path": "nope.md"})],
                       [text_chunk("done")]])
    list(agent.chat("read something"))
    assert agent.llm.tools_offered == [True, True, True]  # list_notes keeps them on; the read_note error does too


def test_made_up_tool_call_is_nudged_not_shown(cfg):
    junk = '{"name": "localize_time", "parameters": {"time": "x"}}'
    agent = make(cfg, [[tool_chunk("get_time", {})], [text_chunk(junk)], [text_chunk("It is noon.")]])
    events = list(agent.chat("time?"))
    tokens = [e["text"] for e in events if e["type"] == "token"]
    assert tokens == ["It is noon."]
    assert all("localize_time" not in str(m.get("content")) for m in agent.messages)  # not kept in history
    assert agent.llm.calls[2][-1]["content"] == agent.NUDGE  # the retry asked for words


def test_made_up_tool_call_twice_gives_plain_fallback(cfg):
    junk = '{"name": "nope", "parameters": {}}'
    agent = make(cfg, [[tool_chunk("get_time", {})], [text_chunk(junk)], [text_chunk(junk)]])
    tokens = [e["text"] for e in agent.chat("time?") if e["type"] == "token"]
    assert tokens == [agent.FALLBACK]


def test_clock_line_is_told_to_the_model_each_round_but_not_stored(cfg):
    llm = FakeLLM([[text_chunk("ok")]])
    agent = Agent(llm, build_registry(cfg), "sys prompt", 4, 40, clock=lambda: "NOW IS NOON")
    list(agent.chat("time?"))
    assert llm.calls[0][0]["content"] == "sys prompt\n\nNOW IS NOON"
    assert agent.messages[0]["content"] == "sys prompt"  # history keeps the plain prompt
