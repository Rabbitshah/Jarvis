"""Load settings from config/jarvis.toml with a few env overrides."""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "jarvis.toml"


@dataclass(frozen=True)
class Config:
    ollama_url: str
    model: str
    embed_model: str
    timeout_seconds: float
    max_tool_rounds: int
    max_history: int
    tool_timeout_seconds: float
    system_prompt: str
    notes_dir: Path
    index_dir: Path
    ingest_exclude: tuple[str, ...]
    private_notes: tuple[str, ...]
    memory_enabled: bool
    memory_k: int
    memory_min_score: float
    memory_chunk_chars: int
    memory_note_header: bool
    memory_doc_prefix: str
    memory_query_prefix: str
    stt: str
    api_host: str
    api_port: int


def load_config(path: str | Path | None = None) -> Config:
    cfg_path = Path(path or os.environ.get("JARVIS_CONFIG") or DEFAULT_CONFIG)
    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    llm, agent, paths, api = data["llm"], data["agent"], data["paths"], data["api"]
    memory = data.get("memory", {})
    voice = data.get("voice", {})

    notes = Path(os.environ.get("JARVIS_NOTES_DIR") or paths["notes_dir"])
    if not notes.is_absolute():
        notes = ROOT / notes

    index = Path(os.environ.get("JARVIS_INDEX_DIR") or paths.get("index_dir", ".tools/qdrant"))
    if not index.is_absolute():
        index = ROOT / index

    return Config(
        ollama_url=os.environ.get("JARVIS_OLLAMA_URL") or llm["ollama_url"],
        model=os.environ.get("JARVIS_MODEL") or llm["model"],
        embed_model=llm["embed_model"],
        timeout_seconds=float(llm["timeout_seconds"]),
        max_tool_rounds=int(agent["max_tool_rounds"]),
        max_history=int(agent["max_history"]),
        tool_timeout_seconds=float(agent.get("tool_timeout_seconds", 10)),
        system_prompt=agent["system_prompt"].strip(),
        notes_dir=notes,
        index_dir=index,
        ingest_exclude=tuple(paths.get("ingest_exclude", [])),
        private_notes=tuple(paths.get("private_notes", [])),
        memory_enabled=bool(memory.get("enabled", True)),
        memory_k=int(memory.get("k", 3)),
        memory_min_score=float(memory.get("min_score", 0.5)),
        memory_chunk_chars=int(memory.get("chunk_chars", 800)),
        memory_note_header=bool(memory.get("note_header", True)),
        memory_doc_prefix=str(memory.get("doc_prefix", "")),
        memory_query_prefix=str(memory.get("query_prefix", "")),
        stt=os.environ.get("JARVIS_STT") or voice.get("stt", "faster:small"),
        api_host=api["host"],
        api_port=int(api["port"]),
    )
