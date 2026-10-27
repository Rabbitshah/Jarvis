"""Show exactly what the model is sent and what it sends back for ONE question.
Use when an answer looks wrong:  scripts/debug-turn.sh "what time is it"
Nothing is saved; notes are only read."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from jarvis.cli import build_agent  # noqa: E402
from jarvis.config import load_config  # noqa: E402


def main() -> int:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('usage: scripts/debug-turn.sh "your question"')
        return 1
    agent, _ = build_agent(load_config())
    real = agent.llm.chat_stream
    n = {"round": 0}

    def spy(messages, tools=None):
        n["round"] += 1
        print(f"\n=== ROUND {n['round']}: sent to the model ({len(messages)} messages) ===")
        for m in messages[1:]:  # skip the long system prompt
            print(f"[{m['role']}] {str(m.get('content'))[:600]!r}" + (f" tool_calls={m['tool_calls']}" if m.get("tool_calls") else ""))
        print(f"--- model replied ---")
        for chunk in real(messages, tools):
            msg = chunk.get("message") or {}
            if msg.get("content"):
                print(repr(msg["content"]), end=" ")
            if msg.get("tool_calls"):
                print("\nTOOL_CALLS:", json.dumps(msg["tool_calls"]))
            yield chunk
        print()

    agent.llm.chat_stream = spy
    for ev in agent.chat(question):
        if ev["type"] == "tool_result":
            print(f"\n=== TOOL RESULT {ev['name']}: {ev['result'][:300]!r}")
        elif ev["type"] == "sources":
            print(f"\n=== notes in context: {ev['files']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
