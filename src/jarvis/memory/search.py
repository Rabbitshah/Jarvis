"""Search the note index by meaning."""
from __future__ import annotations

from typing import Callable

from ..config import Config
from ..tools.notes import is_private
from .store import Hit, StoreError, VectorStore

MAX_QUERY_CHARS = 500
MAX_K = 10
Embed = Callable[[list[str]], list[list[float]]]


def search_notes(cfg: Config, embed: Embed, query: str, k: int = 3) -> list[Hit]:
    query = (query or "").strip()
    if not query:
        raise StoreError("a search query is required")
    if len(query) > MAX_QUERY_CHARS:
        raise StoreError(f"query is too long (max {MAX_QUERY_CHARS} characters)")
    k = max(1, min(int(k), MAX_K))
    if not cfg.index_dir.is_dir():  # do not create an empty index as a side effect of a search
        raise StoreError("The note index does not exist yet. Run scripts/ingest.sh first")
    vector = embed([cfg.memory_query_prefix + query])[0]
    with VectorStore(cfg.index_dir, len(vector)) as store:
        if store.count() == 0:
            raise StoreError("The note index is empty. Run scripts/ingest.sh first")
        hits = store.search(vector, k + 5)  # a few extra, in case stale private hits are dropped below
    return [h for h in hits if not is_private(h.file, cfg.private_notes)][:k]
