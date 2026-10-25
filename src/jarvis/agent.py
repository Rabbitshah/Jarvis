"""Agent loop: stream model output, run tool calls, feed results back."""
from __future__ import annotations

import json
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

    def chat(self, user_text: str) -> Iterator[dict]:
        self.messages.append({"role": "user", "content": user_text})
        self._trim()
        turn = len(self.messages) - 1  # index of this turn's user message
        ctx = self.context_fn(user_text) if self.context_fn else None
        if ctx:
            yield {"type": "sources", "files": ctx.files}
        try:
            for _ in range(self.max_rounds):
                content, calls, held = "", [], False
                view = list(self.messages)
                if ctx:  # excerpts go to the model for THIS turn only; history keeps the plain question
                    view[turn] = {"role": "user", "content": f"{ctx.text}\n\nQuestion: {user_text}"}
                for chunk in self.llm.chat_stream(view, self.registry.schemas()):
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
                        yield {"type": "token", "text": content}

                assistant: dict[str, Any] = {"role": "assistant", "content": content}
                if calls:
                    assistant["tool_calls"] = calls
                self.messages.append(assistant)
                if not calls:
                    yield {"type": "done"}
                    return

                for call in calls:
                    fn = call.get("function") or {}
                    name, args = fn.get("name", ""), fn.get("arguments") or {}
                    yield {"type": "tool_call", "name": name, "args": args}
                    result = self.registry.call(name, args)
                    self.messages.append({"role": "tool", "tool_name": name, "content": result})
                    yield {"type": "tool_result", "name": name, "result": result}
                    if self.proposals:
                        for p in self.proposals.take_new():
                            yield {"type": "confirm", "id": p.id, "fact": p.fact, "from_context": bool(ctx)}
            yield {"type": "error", "message": "tool loop limit reached"}
        except LLMError as exc:
            yield {"type": "error", "message": str(exc)}
