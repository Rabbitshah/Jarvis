"""Thin client for the Ollama HTTP API (/api/chat, /api/embed, /api/tags)."""
from __future__ import annotations

import json
from typing import Iterator

import httpx


class LLMError(RuntimeError):
    """Raised when the model server cannot answer."""


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: float = 120.0,
                 embed_model: str = "nomic-embed-text") -> None:
        self.base_url = base_url
        self.model = model
        self.embed_model = embed_model
        self._http = httpx.Client(base_url=base_url, timeout=timeout)

    def chat_stream(self, messages: list[dict], tools: list[dict] | None = None) -> Iterator[dict]:
        payload: dict = {"model": self.model, "messages": messages, "stream": True}
        if tools:
            payload["tools"] = tools
        try:
            with self._http.stream("POST", "/api/chat", json=payload) as resp:
                if resp.status_code >= 400:
                    resp.read()
                    raise LLMError(f"Ollama returned {resp.status_code}: {resp.text[:300]}")
                for line in resp.iter_lines():
                    if line:
                        yield json.loads(line)
        except httpx.ConnectError as exc:
            raise LLMError(
                f"Cannot reach Ollama at {self.base_url}. Start it with scripts/run.sh"
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMError("Ollama timed out") from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts with the embedding model (POST /api/embed). One vector per text."""
        if not texts:
            return []
        try:
            resp = self._http.post("/api/embed", json={"model": self.embed_model, "input": texts})
        except httpx.ConnectError as exc:
            raise LLMError(f"Cannot reach Ollama at {self.base_url}. Start it with scripts/run.sh") from exc
        except httpx.TimeoutException as exc:
            raise LLMError("Ollama timed out while embedding") from exc
        if resp.status_code == 404:
            raise LLMError(f"Embedding model '{self.embed_model}' is not installed. Run: ollama pull {self.embed_model}")
        if resp.status_code >= 400:
            raise LLMError(f"Ollama returned {resp.status_code}: {resp.text[:300]}")
        vectors = resp.json().get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise LLMError("Ollama returned an unexpected embedding response")
        return vectors

    def list_models(self) -> list[str]:
        try:
            resp = self._http.get("/api/tags")
            resp.raise_for_status()
        except httpx.HTTPError:
            return []
        return [m.get("name", "") for m in resp.json().get("models", [])]

    def ping(self) -> bool:
        try:
            return self._http.get("/api/tags").status_code == 200
        except httpx.HTTPError:
            return False
