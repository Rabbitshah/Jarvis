import dataclasses

import pytest

from jarvis.config import load_config


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
    return dataclasses.replace(load_config(), notes_dir=notes)
