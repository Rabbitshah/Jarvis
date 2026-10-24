"""The built-in tool set. Keep it small: small local models pick tools badly when there are many."""
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
    reg = Registry()

    reg.register(Tool(
        name="get_time",
        description="Get the current local date and time.",
        parameters={"type": "object", "properties": {}},
        fn=_now_text,
    ))
    reg.register(Tool(
        name="list_notes",
        description="List the user's note files (relative paths).",
        parameters={"type": "object", "properties": {}},
        fn=lambda: notes.list_notes(cfg.notes_dir),
    ))
    reg.register(Tool(
        name="read_note",
        description="Read one note by its relative path, as returned by list_notes.",
        parameters={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "relative note path"}},
            "required": ["path"],
        },
        fn=lambda path: notes.read_note(cfg.notes_dir, path),
    ))
    return reg
