"""Agent loop: stream model output, run tool calls, feed results back."""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Iterator, Protocol

from .llm import LLMError
from .tools.registry import Registry


class ChatClient(Protocol):
    def chat_stream(self, messages: list[dict], tools: list[dict] | None = None) -> Iterator[dict]: ...


class Agent:
    def __init__(self, llm: ChatClient, registry: Registry, system_prompt: str,
                 max_rounds: int = 4, max_history: int = 40,
                 context_fn: Callable[[str], Any] | None = None, proposals: Any = None) -> None:
        self.llm = llm
        self.registry = registry
        self.system_prompt = system_prompt
        self.max_rounds = max_rounds
        self.max_history = max_history
        self.context_fn = context_fn
        self.proposals = proposals  # facts waiting for the user's y/n
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    def reset(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def _trim(self) -> None:
        # Drop oldest turns, but always restart at a user message so tool pairs never split.
        while len(self.messages) > self.max_history:
            del self.messages[1]
            while len(self.messages) > 1 and self.messages[1]["role"] != "user":
                del self.messages[1]

    def _text_tool_call(self, content: str) -> dict | None:
        """Small models sometimes print {"name": ..., "parameters": ...} instead of calling the tool."""
        try:
            obj = json.loads(content.strip())
        except json.JSONDecodeError:
            return None
        if not isinstance(obj, dict) or obj.get("name") not in self.registry.names():
            return None
        args = obj.get("parameters", obj.get("arguments", {}))
        return {"function": {"name": obj["name"], "arguments": args if isinstance(args, dict) else {}}}

    ANSWER_KEYS = ("output", "answer", "response", "result", "value", "text", "message")

    @classmethod
    def _unwrap_answer(cls, content: str) -> str:
        """llama3.1 sometimes wraps its final sentence in JSON, e.g. {"output": "It is 11:35 AM"}.
        Seen on Day 25 and it would be read out loud. Unwrap only that small shape; other JSON stays."""
        try:
            obj = json.loads(content.strip())
        except json.JSONDecodeError:
            return content
        if not (isinstance(obj, dict) and 1 <= len(obj) <= 2 and all(isinstance(v, str) for v in obj.values())):
            return content
        for key in cls.ANSWER_KEYS:
            if key in obj and obj[key].strip():
                return obj[key].strip()
        return content

    def chat(self, user_text: str) -> Iterator[dict]:
        self.messages.append({"role": "user", "content": user_text})
        self._trim()
        turn = len(self.messages) - 1  # index of this turn's user message
        ctx = self.context_fn(user_text) if self.context_fn else None
        cited: list[str] = list(ctx.files) if ctx else []  # notes that reached the model this turn
        offer_tools = True
        try:
            for _ in range(self.max_rounds):
                content, calls, held = "", [], False
                view = list(self.messages)
                if ctx:  # excerpts go to the model for THIS turn only; history keeps the plain question
                    view[turn] = {"role": "user", "content": f"{ctx.text}\n\nQuestion: {user_text}"}
                for chunk in self.llm.chat_stream(view, self.registry.schemas() if offer_tools else None):
                    msg = chunk.get("message") or {}
                    text = msg.get("content")
                    if text:
                        if not content and text.lstrip().startswith("{"):
                            held = True  # might be a tool call written as text; decide at the end
                        content += text
                        if not held:
                            yield {"type": "token", "text": text}
                    calls.extend(msg.get("tool_calls") or [])
                if held and not calls:
                    rescued = self._text_tool_call(content)
                    if rescued:
                        calls, content = [rescued], ""
                    else:
                        content = self._unwrap_answer(content)
                        yield {"type": "token", "text": content}

                assistant: dict[str, Any] = {"role": "assistant", "content": content}
                if calls:
                    assistant["tool_calls"] = calls
                self.messages.append(assistant)
                if not calls:
                    if cited:  # the program, not the model, says which notes were consulted
                        yield {"type": "sources", "files": cited}
                    yield {"type": "done"}
                    return

                offer_tools = False  # see below: the answer round gets no tools unless the model must go on
                for call in calls:
                    fn = call.get("function") or {}
                    name, args = fn.get("name", ""), fn.get("arguments") or {}
                    yield {"type": "tool_call", "name": name, "args": args}
                    result = self.registry.call(name, args)
                    self.messages.append({"role": "tool", "tool_name": name, "content": result})
                    yield {"type": "tool_result", "name": name, "result": result}
                    # Day 25-26: with tools still on offer llama3.1 answers in JSON ({"status": "OK", ...}) and
                    # invents fields. So after a tool ran, the next round has no tools, except when the model
                    # has to go on: list_notes (then read_note) or an error (it may retry).
                    if name == "list_notes" or result.startswith("error"):
                        offer_tools = True
                    if name == "search_notes" and result.startswith("Note excerpts"):
                        for f in re.findall(r"^\d+\. (.+?) \(match", result, re.MULTILINE):
                            if f not in cited:
                                cited.append(f)
                    if self.proposals:
                        for p in self.proposals.take_new():
                            yield {"type": "confirm", "id": p.id, "fact": p.fact, "from_context": bool(ctx)}
            yield {"type": "error", "message": "tool loop limit reached"}
        except LLMError as exc:
            yield {"type": "error", "message": str(exc)}
