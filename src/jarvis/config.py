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
    api_host: str
    api_port: int


def load_config(path: str | Path | None = None) -> Config:
    cfg_path = Path(path or os.environ.get("JARVIS_CONFIG") or DEFAULT_CONFIG)
    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    llm, agent, paths, api = data["llm"], data["agent"], data["paths"], data["api"]

    notes = Path(os.environ.get("JARVIS_NOTES_DIR") or paths["notes_dir"])
    if not notes.is_absolute():
        notes = ROOT / notes

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
        api_host=api["host"],
        api_port=int(api["port"]),
    )
