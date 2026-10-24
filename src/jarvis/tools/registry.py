"""Tool registry. Agent and (later) MCP server both use these same tools."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

log = logging.getLogger(__name__)


class ToolError(Exception):
    """Expected, user-safe tool failure. Message goes back to the model."""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict
    fn: Callable[..., str]


class Registry:
    def __init__(self) -> None:
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
            return f"error: unknown tool '{name}'"
        if isinstance(args, str):
            try:
                args = json.loads(args or "{}")
            except json.JSONDecodeError:
                return "error: tool arguments are not valid JSON"
        if not isinstance(args, dict):
            return "error: tool arguments must be an object"
        try:
            return str(tool.fn(**args))
        except ToolError as exc:
            return f"error: {exc}"
        except TypeError as exc:
            return f"error: bad arguments ({exc})"
        except Exception:  # noqa: BLE001 - never crash the agent loop
            log.exception("tool %s failed", name)
            return "error: tool failed unexpectedly"
