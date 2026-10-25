import dataclasses
from pathlib import Path

import pytest

from jarvis.config import ROOT, load_config

REAL_DATA = (ROOT / "notes", ROOT / ".tools" / "qdrant")  # your real notes and your real index


def fingerprint(path: Path) -> list[tuple]:
    """Name, size and modification time of every file under path (empty if it does not exist)."""
    if not path.exists():
        return []
    return sorted((str(p.relative_to(path)), p.stat().st_size, p.stat().st_mtime_ns)
                  for p in path.rglob("*") if p.is_file())


@pytest.fixture(scope="session", autouse=True)
def real_data_untouched():
    """Fails the test run if any test changed your real notes or your real index."""
    before = [fingerprint(p) for p in REAL_DATA]
    yield
    after = [fingerprint(p) for p in REAL_DATA]
    for path, b, a in zip(REAL_DATA, before, after):
        assert a == b, f"a test changed real data in {path}"


@pytest.fixture(autouse=True)
def isolated_data(monkeypatch, tmp_path_factory):
    """Every test (and every subprocess it starts) gets its own empty notes and index folders."""
    base = tmp_path_factory.mktemp("jarvis-data")
    monkeypatch.setenv("JARVIS_NOTES_DIR", str(base / "notes"))
    monkeypatch.setenv("JARVIS_INDEX_DIR", str(base / "index"))


class FakeLLM:
    """Replays scripted rounds. Each round is a list of Ollama-style chunks."""

    def __init__(self, rounds):
        self.rounds = list(rounds)
        self.calls = []

    def chat_stream(self, messages, tools=None):
        self.calls.append([dict(m) for m in messages])
        yield from self.rounds.pop(0)

    def ping(self):
        return True


def text_chunk(text):
    return {"message": {"role": "assistant", "content": text}}


def tool_chunk(name, args):
    return {"message": {"role": "assistant", "content": "",
                        "tool_calls": [{"function": {"name": name, "arguments": args}}]}}


@pytest.fixture
def cfg(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "idea.md").write_text("Ship Jarvis by December.", encoding="utf-8")
    return dataclasses.replace(load_config(), notes_dir=notes, index_dir=tmp_path / "index")
