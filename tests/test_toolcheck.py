import re
from datetime import datetime

from conftest import FakeLLM, text_chunk, tool_chunk
from jarvis import toolcheck
from jarvis.agent import Agent
from jarvis.tools.builtin import build_registry

NOW = datetime(2026, 10, 27, 15, 40).astimezone()


def test_clock_accepts_both_clocks_and_rejects_wrong():
    ok = toolcheck.clock_problem
    assert ok("It is 3:40 PM", NOW) is None and ok("It is 15:41", NOW) is None
    assert ok("It is 3:30 PM", NOW) is not None and ok("It is 4:40 PM", NOW) is not None
    assert ok("no digits", NOW) is not None


def test_date_check():
    assert toolcheck.date_problem("It is 27 October 2026", NOW) is None
    assert toolcheck.date_problem("October 28th", NOW) is not None


def case(name):
    return next(c for c in toolcheck.builtin_cases(NOW) if c.name == name)


def test_judge_rules():
    j = toolcheck.judge
    assert j(case("capital"), "Paris.", [], []) is None
    assert "JSON" in j(case("capital"), '{"a": "Paris"}', [], [])
    assert "own steps" in j(case("capital"), "The tool call returns Paris", [], [])
    assert "should not be used" in j(case("capital"), "Paris", ["search_notes"], [])
    assert "not called" in j(case("remember"), "Okay.", [], [])
    assert j(case("remember"), "Okay.", ["remember"], []) is None
    assert j(case("time"), "It is 3:40 PM", [], []) is None  # told in the prompt, no tool needed
    assert j(case("calendar"), "You have a meeting tonight.", [], []) is not None
    assert j(case("calendar"), "I can't see your calendar.", [], []) is None
    assert j(case("weather"), "It is sunny, 30 degrees.", [], []) is not None
    assert j(case("weather"), "", [], []) == "empty answer"


def test_notes_cases_check_sources():
    c = toolcheck.notes_cases([{"question": "q?", "note": ["a.md", "b.md"]}])[0]
    assert toolcheck.judge(c, "answer", [], ["b.md"]) is None
    assert "right note" in toolcheck.judge(c, "answer", [], ["z.md"])


def test_run_case_with_fake_model(cfg):
    llm = FakeLLM([[tool_chunk("get_time", {})], [text_chunk("It is 3:40 PM.")]])
    new = lambda: Agent(llm, build_registry(cfg), "sys", 4, 40)  # noqa: E731
    out = toolcheck.run_case(new, case("time"), lambda: 0.0)
    assert out.ok and out.answer == "It is 3:40 PM."


def test_answer_and_tool_verdicts_are_separate():
    a, t = toolcheck.judge_parts(case("capital"), "Paris.", ["search_notes"], [])
    assert a is None and "should not be used" in t
    a, t = toolcheck.judge_parts(case("math"), "It is 379", [], [])
    assert a is not None and t is None
