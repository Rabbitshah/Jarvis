"""Score how reliably a model answers through the agent: right tool, plain words, no invented facts."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

META = re.compile(r"\b(the tool call|tool call returns|i will use this|here is the answer)\b", re.IGNORECASE)
CANNOT = re.compile(r"\b(can't|cannot|can not|don't have|do not have|no access|unable|not able|couldn't find|"
                    r"could not find|don't know|no (?:notes|information))\b", re.IGNORECASE)


@dataclass
class Case:
    name: str
    question: str
    tools: set[str] | None = None          # tools that must all be called
    forbid_tools: set[str] = field(default_factory=set)
    must: re.Pattern | None = None          # answer must match
    must_not: re.Pattern | None = None      # answer must not match
    check: Callable[[str, list[str], list[str]], str | None] | None = None  # (answer, tools, sources) -> problem


@dataclass(frozen=True)
class Outcome:
    case: str
    ok: bool            # answer correct AND the right tools used (strict)
    problem: str
    answer: str
    seconds: float
    answer_ok: bool = True   # answer correct, whatever tools were used


def clock_problem(answer: str, now: datetime) -> str | None:
    """The answer must contain the current time (12 or 24 hour clock, within 2 minutes)."""
    for h, m in re.findall(r"(\d{1,2})[:.](\d{2})", answer):
        h, m = int(h), int(m)
        if h % 12 == now.hour % 12 and min((m - now.minute) % 60, (now.minute - m) % 60) <= 2:
            return None
    return f"no correct time in answer (now {now:%H:%M})"


def date_problem(answer: str, now: datetime) -> str | None:
    if now.strftime("%B").lower() in answer.lower() and re.search(rf"\b{now.day}(st|nd|rd|th)?\b", answer):
        return None
    return f"no correct date in answer (today {now:%d %B})"


def builtin_cases(now: datetime) -> list[Case]:
    return [
        Case("time", "what time is it", check=lambda a, t, s: clock_problem(a, now)),
        Case("date", "what is today's date", check=lambda a, t, s: date_problem(a, now)),
        Case("fun fact", "tell me a fun fact", forbid_tools={"search_notes", "read_note", "list_notes", "remember"},
             must_not=re.compile(r"pickleball|grad school|jarvis project", re.IGNORECASE)),
        Case("capital", "what is the capital of France", forbid_tools={"search_notes", "read_note", "list_notes", "remember"},
             must=re.compile(r"paris", re.IGNORECASE)),
        Case("math", "what is 17 times 23", forbid_tools={"search_notes", "read_note", "remember"},
             must=re.compile(r"\b391\b")),
        Case("explain", "explain what an API is in two sentences",
             forbid_tools={"search_notes", "read_note", "list_notes", "remember"}, must=re.compile(r"interface|request|software", re.IGNORECASE)),
        Case("calendar", "do I have any meetings tonight", must=CANNOT,
             must_not=re.compile(r"you have (a|an|one|\d+) (\w+ )?meeting", re.IGNORECASE)),
        Case("weather", "what is the weather in Vadodara today", must=CANNOT,
             must_not=re.compile(r"\b\d+\s*°|degrees|sunny|cloudy|rain", re.IGNORECASE)),
        Case("remember", "remember that my favourite colour is green", tools={"remember"}),
    ]


def notes_cases(raw: list[dict], limit: int = 5) -> list[Case]:
    def make(entry: dict) -> Case:
        wanted = entry["note"] if isinstance(entry["note"], list) else [entry["note"]]

        def check(answer: str, tools: list[str], sources: list[str]) -> str | None:
            return None if any(w in sources for w in wanted) else f"right note not consulted (got {sources or 'none'})"

        return Case("notes: " + entry["question"][:40], entry["question"], check=check)

    return [make(e) for e in raw[:limit]]


def run_case(new_agent: Callable[[], object], case: Case, clock: Callable[[], float]) -> Outcome:
    agent = new_agent()
    answer, tools, sources = "", [], []
    start = clock()
    for ev in agent.chat(case.question):
        if ev["type"] == "token":
            answer += ev["text"]
        elif ev["type"] == "tool_call":
            tools.append(ev["name"])
        elif ev["type"] == "sources":
            sources = ev["files"]
        elif ev["type"] == "error":
            return Outcome(case.name, False, f"error: {ev['message']}", answer, clock() - start)
    took = clock() - start
    answer = answer.strip()
    a_problem, t_problem = judge_parts(case, answer, tools, sources)
    problem = a_problem or t_problem
    return Outcome(case.name, problem is None, problem or "", answer, took, answer_ok=a_problem is None)


def judge_parts(case: Case, answer: str, tools: list[str], sources: list[str]) -> tuple[str | None, str | None]:
    """(problem with the answer itself, problem with how the tools were used)."""
    a = None
    if not answer:
        a = "empty answer"
    elif answer.startswith(("{", "[")):
        a = "answer is JSON"
    elif META.search(answer):
        a = "answer talks about its own steps"
    elif case.must and not case.must.search(answer):
        a = "answer missing the expected content"
    elif case.must_not and case.must_not.search(answer):
        a = "answer contains something invented or off-topic"
    elif case.check:
        a = case.check(answer, tools, sources)
    t = None
    if case.tools and not case.tools <= set(tools):
        t = f"tool not called: {sorted(case.tools - set(tools))}"
    elif case.forbid_tools & set(tools):
        t = f"tool should not be used: {sorted(case.forbid_tools & set(tools))}"
    return a, t


def judge(case: Case, answer: str, tools: list[str], sources: list[str]) -> str | None:
    a, t = judge_parts(case, answer, tools, sources)
    return a or t
