"""Sandboxed access to the notes folder. Nothing outside it is ever readable."""
from __future__ import annotations

import fnmatch
from pathlib import Path

from .registry import ToolError

ALLOWED_SUFFIXES = {".md", ".txt"}
MAX_CHARS = 20_000
MAX_LIST = 200


def resolve_note(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel.strip() or "\x00" in rel:
        raise ToolError("a note path is required")
    candidate = Path(rel)
    if candidate.is_absolute():
        raise ToolError("absolute paths are not allowed")
    root_resolved = root.resolve()
    full = (root_resolved / candidate).resolve()  # resolves symlinks and ..
    if not full.is_relative_to(root_resolved):
        raise ToolError("path escapes the notes folder")
    if full.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ToolError("not a valid note name; use a full file name ending in .md or .txt. Call list_notes to see the exact names")
    return full


def is_private(rel: str, patterns: tuple[str, ...]) -> bool:
    """True if a note matches a private pattern. Matching is on the lower-case path inside notes/."""
    low = rel.replace("\\", "/").lower()
    return any(fnmatch.fnmatchcase(low, pat.lower()) for pat in patterns)


def _note_files(root: Path, private: tuple[str, ...] = ()) -> list[str]:
    root_resolved = root.resolve()
    if not root_resolved.is_dir():
        raise ToolError("notes folder does not exist")
    found = [
        str(p.relative_to(root_resolved))
        for p in root_resolved.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES and p.resolve().is_relative_to(root_resolved)
    ]
    return sorted(f for f in found if not is_private(f, private))


def list_notes(root: Path, private: tuple[str, ...] = ()) -> str:
    found = _note_files(root, private)
    if not found:
        return "no notes found"
    extra = f"\n(+{len(found) - MAX_LIST} more not shown)" if len(found) > MAX_LIST else ""
    return "\n".join(found[:MAX_LIST]) + extra


def _expand_plain_name(root: Path, path: str, private: tuple[str, ...] = ()) -> str:
    """'Falcon' or 'Falcon.txt' -> the one note whose name contains it. Plain names only."""
    if not isinstance(path, str) or not path.strip() or path != Path(path).name or path in (".", ".."):
        return path
    if (root / path).is_file() and Path(path).suffix.lower() in ALLOWED_SUFFIXES:
        return path
    query = Path(path).stem.lower()
    matches = [n for n in _note_files(root, private) if query and query in Path(n).stem.lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ToolError("several notes match: " + ", ".join(matches) + ". Use the exact name")
    return path


def read_note(root: Path, path: str, private: tuple[str, ...] = ()) -> str:
    full = resolve_note(root, _expand_plain_name(root, path, private))
    # a private note answers exactly like a missing one, so its existence is not revealed
    if not full.is_file() or is_private(str(full.relative_to(root.resolve())), private):
        raise ToolError("note not found. Call list_notes to see the exact names")
    with full.open(encoding="utf-8", errors="replace") as handle:
        text = handle.read(MAX_CHARS + 1)  # never load a huge file into memory
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + f"\n\n[truncated at {MAX_CHARS} characters]"
    return text
