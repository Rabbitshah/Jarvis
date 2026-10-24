"""The single tool set. The agent and the MCP server both register these exact functions.

Keep it small: small local models pick tools badly when there are many.
Type hints matter: the MCP server builds its input schema from them.
"""
from __future__ import annotations

from datetime import datetime

from ..config import Config
from . import notes
from .registry import Registry, Tool


def _now_text() -> str:
    # Plain words, 12-hour clock: raw ISO strings get misread by small models.
    now = datetime.now().astimezone()
    return f"It is {now:%A, %d %B %Y}, {now:%I:%M %p}, local time."


def build_registry(cfg: Config) -> Registry:
    def get_time() -> str:
        return _now_text()

    def list_notes() -> str:
        return notes.list_notes(cfg.notes_dir)

    def read_note(path: str) -> str:
        return notes.read_note(cfg.notes_dir, path)

    reg = Registry()
    reg.register(Tool(
        name="get_time",
        description="Get the current local date and time.",
        parameters={"type": "object", "properties": {}},
        fn=get_time,
    ))
    reg.register(Tool(
        name="list_notes",
        description="List the user's note files (relative paths).",
        parameters={"type": "object", "properties": {}},
        fn=list_notes,
    ))
    reg.register(Tool(
        name="read_note",
        description="Read one note by its relative path, as returned by list_notes.",
        parameters={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "relative note path"}},
            "required": ["path"],
        },
        fn=read_note,
    ))
    return reg
