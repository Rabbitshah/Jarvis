"""Read the notes, chunk them, embed them, and store them.

Incremental: each file is hashed together with the settings that affect embedding. Only files whose
hash changed are embedded again; files that disappeared from notes/ are removed from the index."""
from __future__ import annotations

import fnmatch
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..config import Config
from ..tools.notes import _note_files, read_note
from .chunker import chunk_text
from .store import NoIndex, VectorStore

BATCH = 16
Embed = Callable[[list[str]], list[list[float]]]


@dataclass
class IngestResult:
    files: dict[str, int] = field(default_factory=dict)  # every indexed note -> its chunk count
    skipped: list[str] = field(default_factory=list)     # excluded or empty files
    unchanged: list[str] = field(default_factory=list)   # notes not embedded again
    removed: list[str] = field(default_factory=list)     # notes dropped from the index
    embedded: int = 0                                    # chunks embedded in THIS run
    stored_total: int = 0                                # points in the index afterwards

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


def file_digest(cfg: Config, max_chars: int, text: str) -> str:
    """Changes when the note changes OR any setting that changes its embedding."""
    settings = "|".join([cfg.embed_model, str(max_chars), str(cfg.memory_note_header), cfg.memory_doc_prefix])
    return hashlib.sha256(f"{settings}\0{text}".encode("utf-8")).hexdigest()


def ingest(cfg: Config, embed: Embed, max_chars: int | None = None, full: bool = False) -> IngestResult:
    max_chars = max_chars or cfg.memory_chunk_chars
    result = IngestResult()
    plan: dict[str, tuple[list[str], str]] = {}  # name -> (chunks, digest)
    for name in _note_files(cfg.notes_dir, cfg.private_notes):  # private notes are never indexed
        if _skip(name, cfg.ingest_exclude):
            result.skipped.append(name)
            continue
        text = read_note(cfg.notes_dir, name)
        chunks = chunk_text(text, max_chars)
        if chunks:
            plan[name] = (chunks, file_digest(cfg, max_chars, text))
        else:
            result.skipped.append(name)
    result.files = {n: len(c) for n, (c, _d) in plan.items()}

    store: VectorStore | None = None
    known: dict[str, str | None] = {}
    if cfg.index_dir.is_dir():
        try:
            store = VectorStore(cfg.index_dir, None).__enter__()
            known = store.file_hashes()
        except NoIndex:
            store = None
    try:
        changed = [n for n in plan if full or known.get(n) != plan[n][1]]
        result.removed = sorted(f for f in known if f not in plan)
        result.unchanged = [n for n in plan if n not in changed]

        flat = [(f, i, c) for f in changed for i, c in enumerate(plan[f][0])]
        vectors: list[list[float]] = []
        for start in range(0, len(flat), BATCH):
            batch = flat[start:start + BATCH]
            vectors.extend(embed([embed_text(f, c, cfg.memory_note_header, cfg.memory_doc_prefix)
                                  for f, _i, c in batch]))
        result.embedded = len(flat)

        if store is None and flat:
            store = VectorStore(cfg.index_dir, len(vectors[0])).__enter__()
        if store is not None:
            for name in changed + result.removed:
                store.delete_file(name)  # also drops chunks left over from a longer older version
            store.upsert([(f, i, c, v) for (f, i, c), v in zip(flat, vectors)],
                         {n: plan[n][1] for n in changed})
            result.stored_total = store.count()
    finally:
        if store is not None:
            store.close()
    return result
