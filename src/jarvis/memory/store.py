"""Local vector store on embedded Qdrant (no server, no Docker).

Embedded Qdrant locks its folder to ONE process at a time, so open the store only
for the moment you need it: `with VectorStore(path, dim) as store: ...`.
The index can always be rebuilt from the notes, so deleting the folder is safe.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from qdrant_client import QdrantClient, models

COLLECTION = "notes"


class StoreError(RuntimeError):
    """Clear, user-safe store problem."""


@dataclass(frozen=True)
class Hit:
    file: str
    chunk: int
    text: str
    score: float


def point_id(file: str, chunk: int) -> str:
    """Same file + chunk number always gives the same id, so re-ingest overwrites."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"jarvis-note:{file}#{chunk}"))


class VectorStore:
    def __init__(self, path: str | Path, dim: int, collection: str = COLLECTION) -> None:
        if dim < 1:
            raise StoreError("vector size must be at least 1")
        self.path, self.dim, self.collection = Path(path), dim, collection
        self._client: QdrantClient | None = None

    def __enter__(self) -> "VectorStore":
        self.path.mkdir(parents=True, exist_ok=True)
        try:
            self._client = QdrantClient(path=str(self.path))
        except RuntimeError as exc:  # folder lock held by another process
            raise StoreError("The note index is in use by another Jarvis process. Try again in a moment") from exc
        self._ensure()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _ensure(self) -> None:
        c = self._need()
        if not c.collection_exists(self.collection):
            c.create_collection(self.collection, vectors_config=models.VectorParams(
                size=self.dim, distance=models.Distance.COSINE))
            return
        have = c.get_collection(self.collection).config.params.vectors.size
        if have != self.dim:
            raise StoreError(
                f"The index holds {have}-number vectors but the embedding model gives {self.dim}. "
                "The embedding model changed: delete the index folder and ingest again")

    def _need(self) -> QdrantClient:
        if self._client is None:
            raise StoreError("store is not open")
        return self._client

    def upsert(self, items: list[tuple[str, int, str, list[float]]]) -> None:
        """items = (file, chunk_number, text, vector)."""
        for file, chunk, _text, vector in items:
            if len(vector) != self.dim:
                raise StoreError(f"vector for {file}#{chunk} has size {len(vector)}, expected {self.dim}")
        points = [models.PointStruct(id=point_id(f, n), vector=v, payload={"file": f, "chunk": n, "text": t})
                  for f, n, t, v in items]
        if points:
            self._need().upsert(self.collection, points=points)

    def search(self, vector: list[float], k: int = 3) -> list[Hit]:
        if len(vector) != self.dim:
            raise StoreError(f"query vector has size {len(vector)}, expected {self.dim}")
        res = self._need().query_points(self.collection, query=vector, limit=max(1, k), with_payload=True)
        return [Hit(p.payload["file"], p.payload["chunk"], p.payload["text"], float(p.score)) for p in res.points]

    def count(self) -> int:
        return self._need().count(self.collection).count

    def delete_file(self, file: str) -> None:
        self._need().delete(self.collection, points_selector=models.FilterSelector(
            filter=models.Filter(must=[models.FieldCondition(key="file", match=models.MatchValue(value=file))])))
