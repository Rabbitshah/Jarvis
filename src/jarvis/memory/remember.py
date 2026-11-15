"""Long-term facts. The model can only PROPOSE a fact. Writing happens in approve(),
which only the interface (terminal y/n prompt, API /confirm) can call, never a tool.
So a note that tries to trick the model cannot save anything on its own."""
from __future__ import annotations

import os
import re
import secrets
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from ..config import Config
from ..llm import LLMError
from ..tools.registry import ToolError
from .ingest import ingest
from .store import StoreError

MEMORY_FILE = "memory.md"
MAX_FACT = 300
MAX_PENDING = 10
TTL_SECONDS = 15 * 60
MAX_FILE_CHARS = 20000
HEADER = "# Memory\n\nFacts Jarvis was asked to remember. One per line. Edit or delete lines freely.\n\n"


@dataclass
class Proposal:
    id: str
    fact: str
    created: float
    announced: bool = False


def clean_fact(fact: str) -> str:
    """One plain line: no newlines, no leading markdown markers that could change the file's structure."""
    text = re.sub(r"\s+", " ", fact or "").strip()
    text = re.sub(r"^[#>*\-\s]+", "", text)
    if not text:
        raise ToolError("the fact is empty")
    if len(text) > MAX_FACT:
        raise ToolError(f"the fact is too long (max {MAX_FACT} characters); shorten it")
    return text


_ASK = re.compile(r"^\s*(?:(?:please|hey|ok(?:ay)?)[\s,]+)*remember\s+(?:that\s+)?(?P<fact>\S.{2,299}?)\s*[.!]?\s*$",
                 re.IGNORECASE | re.DOTALL)
_PERSON = [(r"\bI am\b", "you are"), (r"\bI'm\b", "you're"), (r"\bI've\b", "you've"), (r"\bI'll\b", "you'll"),
           (r"\bI'd\b", "you'd"), (r"\bI\b", "you"), (r"\bmyself\b", "yourself"), (r"\bmine\b", "yours"),
           (r"\bmy\b", "your"), (r"\bme\b", "you")]


def explicit_request(text: str) -> str | None:
    """'Remember that I like green tea.' -> 'You like green tea'. None if this is not a plain
    remember-request. Decided by code, not by the model: the model skipped the tool 2 times in 3 (Day 27b)."""
    m = _ASK.match(text or "")
    if not m:
        return None
    fact = m.group("fact").strip()
    for pattern, repl in _PERSON:
        fact = re.sub(pattern, repl, fact)
    return fact[0].upper() + fact[1:]


_UNDO = re.compile(r"^\s*(?:(?:please|hey|ok(?:ay)?)[\s,]+)*(?:forget\s+(?:that|it)|undo(?:\s+that)?|never\s?mind\s+that)\s*[.!?,]*\s*$",
                  re.IGNORECASE)


def undo_request(text: str) -> bool:
    """'forget that', 'forget it', 'undo', 'undo that', 'never mind that' (decided by code, like explicit_request)."""
    return bool(_UNDO.match(text or ""))


class Proposals:
    def __init__(self, cfg: Config, embed: Callable[[list[str]], list[list[float]]] | None,
                 clock: Callable[[], float] = time.time) -> None:
        self.cfg, self.embed, self._clock = cfg, embed, clock
        self._items: dict[str, Proposal] = {}
        self.saved: list[tuple[str, str]] = []  # (fact, exact memory.md line) written by THIS session: all that undo may touch

    def _drop_expired(self) -> None:
        now = self._clock()
        for pid in [p for p, it in self._items.items() if now - it.created > TTL_SECONDS]:
            del self._items[pid]

    def add(self, fact: str) -> Proposal:
        text = clean_fact(fact)
        self._drop_expired()
        if len(self._items) >= MAX_PENDING:
            raise ToolError("too many facts are waiting for approval; ask the user to answer them first")
        item = Proposal(secrets.token_hex(4), text, self._clock())
        self._items[item.id] = item
        return item

    def take_new(self) -> list[Proposal]:
        """Proposals not yet shown to the user (each is returned once)."""
        self._drop_expired()
        fresh = [p for p in self._items.values() if not p.announced]
        for p in fresh:
            p.announced = True
        return fresh

    def pending(self) -> list[Proposal]:
        self._drop_expired()
        return list(self._items.values())

    def reject(self, pid: str) -> str:
        return "Not saved." if self._items.pop(pid, None) else "That proposal no longer exists."

    def approve(self, pid: str) -> str:
        self._drop_expired()
        item = self._items.pop(pid, None)
        if item is None:
            return "That proposal expired or does not exist. Ask Jarvis to remember it again."
        root = self.cfg.notes_dir
        root.mkdir(parents=True, exist_ok=True)
        path = root / MEMORY_FILE
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            return "Not saved: the memory file is not safe to write."
        text = path.read_text(encoding="utf-8") if path.exists() else HEADER
        if f": {item.fact}\n" in text:
            return "Already remembered."
        line = f"- {datetime.now().astimezone():%Y-%m-%d}: {item.fact}\n"
        if len(text) + len(line) > MAX_FILE_CHARS:
            return f"Not saved: {MEMORY_FILE} is full. Trim old lines first."
        path.write_text(text + line, encoding="utf-8")
        self.saved.append((item.fact, line))
        warn = self._reindex()
        if warn is None:
            return f"Saved to {MEMORY_FILE}."
        return f"Saved to {MEMORY_FILE}. {warn}" if self.embed is None else f"Saved to {MEMORY_FILE}, but {warn}"

    def _reindex(self, saving: bool = True) -> str | None:
        """None if the search index is up to date, else what the user should know."""
        if self.embed is None:
            return "Run scripts/ingest.sh so search " + ("can find it." if saving else "stops returning it.")
        try:
            ingest(self.cfg, self.embed)
        except (LLMError, StoreError) as exc:
            return f"the search index was not updated ({exc}). Run scripts/ingest.sh."
        return None

    def forget_last(self) -> str:
        """Remove the last line THIS session saved. Never any other line."""
        if not self.saved:
            return "Nothing to undo."
        fact, line = self.saved.pop()
        root = self.cfg.notes_dir
        path = root / MEMORY_FILE
        if not path.exists() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            return "Could not undo: the memory file is missing or not safe to write."
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        if line not in lines:
            return f"Could not undo: that line is no longer in {MEMORY_FILE} (you edited it?)."
        del lines[len(lines) - 1 - lines[::-1].index(line)]
        tmp = path.with_name(MEMORY_FILE + ".tmp")
        tmp.write_text("".join(lines), encoding="utf-8")
        os.replace(tmp, path)  # atomic: the file is never half written
        warn = self._reindex(saving=False)
        return f"Removed: {fact}" if warn is None else f"Removed: {fact}. {warn[0].upper()}{warn[1:]}"
