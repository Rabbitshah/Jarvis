"""Tool registry. Agent and MCP server both use these same tools."""
from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass
from typing import Any, Callable

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10.0
_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="jarvis-tool")
_JSON_TYPES: dict[str, type | tuple[type, ...]] = {
    "string": str, "integer": int, "number": (int, float),
    "boolean": bool, "object": dict, "array": list,
}


class ToolError(Exception):
    """Expected, user-safe tool failure. Message goes back to the model."""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict
    fn: Callable[..., str]


def run_with_timeout(fn: Callable[..., Any], seconds: float, **kwargs: Any) -> Any:
    """Run fn in a worker thread. A thread cannot be killed, so a stuck tool keeps its
    thread until it ends, but the caller gets a clear error after `seconds`."""
    future = _POOL.submit(fn, **kwargs)
    try:
        return future.result(timeout=seconds)
    except FutureTimeout:
        if future.done():  # the tool itself raised TimeoutError
            raise
        future.cancel()
        raise ToolError(f"tool timed out after {seconds:g}s") from None


def coerce_args(tool: Tool, args: dict) -> dict:
    """Small models often send numbers as strings ("10"). Convert those; leave everything else to check_args."""
    props = tool.parameters.get("properties", {})
    out = dict(args)
    for name, value in args.items():
        kind = props.get(name, {}).get("type")
        if isinstance(value, str) and kind == "integer" and value.strip().lstrip("-").isdigit():
            out[name] = int(value)
        elif isinstance(value, str) and kind == "number":
            try:
                out[name] = float(value)
            except ValueError:
                pass
    return out


def check_args(tool: Tool, args: dict) -> str | None:
    """Return a problem description, or None. Checks required, unknown and basic types."""
    props = tool.parameters.get("properties", {})
    for name in tool.parameters.get("required", []):
        if name not in args:
            return f"missing required argument '{name}'"
    for name, value in args.items():
        if name not in props:
            allowed = ", ".join(props) or "none"
            return f"unexpected argument '{name}' (allowed: {allowed})"
        kind = props[name].get("type")
        want = _JSON_TYPES.get(kind)
        if want and (not isinstance(value, want) or (isinstance(value, bool) and kind != "boolean")):
            return f"argument '{name}' must be of type {kind}"
    return None


class Registry:
    def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def tools(self) -> list[Tool]:
        return [self._tools[n] for n in sorted(self._tools)]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def schemas(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {"name": t.name, "description": t.description, "parameters": t.parameters},
            }
            for t in self._tools.values()
        ]

    def call(self, name: str, args: Any) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"error: unknown tool '{name}'. Available: {', '.join(self.names())}"
        if isinstance(args, str):
            try:
                args = json.loads(args or "{}")
            except json.JSONDecodeError:
                return "error: tool arguments are not valid JSON"
        if not isinstance(args, dict):
            return "error: tool arguments must be an object"
        args = coerce_args(tool, args)
        problem = check_args(tool, args)
        if problem:
            return f"error: {problem}"
        try:
            return str(run_with_timeout(tool.fn, self.timeout, **args))
        except ToolError as exc:
            return f"error: {exc}"
        except Exception:  # noqa: BLE001 - never crash the agent loop
            log.exception("tool %s failed", name)
            return "error: tool failed unexpectedly"
