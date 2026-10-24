"""Read the notes, chunk them, embed them, and store them. Full re-ingest for now
(incremental by file hash comes in week 4)."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..config import Config
from ..tools.notes import _note_files, read_note
from .chunker import chunk_text
from .store import VectorStore

BATCH = 16
Embed = Callable[[list[str]], list[list[float]]]


@dataclass
class IngestResult:
    files: dict[str, int] = field(default_factory=dict)  # file -> chunks stored
    skipped: list[str] = field(default_factory=list)
    stored_total: int = 0  # points in the index afterwards

    @property
    def chunks(self) -> int:
        return sum(self.files.values())


def _skip(name: str, patterns: tuple[str, ...]) -> bool:
    base = Path(name).name
    return any(fnmatch.fnmatch(base, p) or fnmatch.fnmatch(name, p) for p in patterns)


def embed_text(file: str, chunk: str, header: bool = True, prefix: str = "") -> str:
    """The file name goes into the embedded text so a question naming a topic finds its note."""
    body = f"Note: {Path(file).stem}\n\n{chunk}" if header else chunk
    return prefix + body


def ingest(cfg: Config, embed: Embed, max_chars: int | None = None) -> IngestResult:
    max_chars = max_chars or cfg.memory_chunk_chars
    result = IngestResult()
    plan: list[tuple[str, list[str]]] = []
    for name in _note_files(cfg.notes_dir):
        if _skip(name, cfg.ingest_exclude):
            result.skipped.append(name)
            continue
        chunks = chunk_text(read_note(cfg.notes_dir, name), max_chars)
        if chunks:
            plan.append((name, chunks))
        else:
            result.skipped.append(name)

    flat = [(f, i, c) for f, chunks in plan for i, c in enumerate(chunks)]
    vectors: list[list[float]] = []
    for start in range(0, len(flat), BATCH):
        batch = flat[start:start + BATCH]
        vectors.extend(embed([embed_text(f, c, cfg.memory_note_header, cfg.memory_doc_prefix) for f, _i, c in batch]))
    if not flat:
        return result
    dim = len(vectors[0])

    with VectorStore(cfg.index_dir, dim) as store:
        for name, _chunks in plan:
            store.delete_file(name)  # drops chunks left over from a longer older version
        store.upsert([(f, i, c, v) for (f, i, c), v in zip(flat, vectors)])
        result.stored_total = store.count()
    for f, _i, _c in flat:
        result.files[f] = result.files.get(f, 0) + 1
    return result
