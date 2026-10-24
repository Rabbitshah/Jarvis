"""Terminal chat and a small doctor check."""
from __future__ import annotations

import argparse
import sys

from .agent import Agent
from .config import load_config
from .llm import OllamaClient
from .tools.builtin import build_registry


def doctor() -> int:
    cfg = load_config()
    llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds)
    ok = True
    print(f"config model     : {cfg.model}")
    print(f"ollama url       : {cfg.ollama_url}")
    if llm.ping():
        print("ollama           : reachable")
        have = cfg.model in llm.list_models()
        print(f"model installed  : {'yes' if have else 'NO (run scripts/setup.sh)'}")
        ok &= have
    else:
        print("ollama           : NOT reachable (run scripts/run.sh)")
        ok = False
    print(f"notes folder     : {cfg.notes_dir} ({'ok' if cfg.notes_dir.is_dir() else 'missing'})")
    print(f"tools            : {', '.join(build_registry(cfg).names())}")
    return 0 if ok else 1


def chat_loop() -> int:
    cfg = load_config()
    llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds)
    agent = Agent(llm, build_registry(cfg), cfg.system_prompt, cfg.max_tool_rounds, cfg.max_history)
    print(f"Jarvis ({cfg.model}). /reset clears memory, /exit quits.")
    while True:
        try:
            text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not text:
            continue
        if text == "/exit":
            return 0
        if text == "/reset":
            agent.reset()
            print("history cleared")
            continue
        print("jarvis> ", end="", flush=True)
        for ev in agent.chat(text):
            if ev["type"] == "token":
                print(ev["text"], end="", flush=True)
            elif ev["type"] == "tool_call":
                print(f"\n  [tool] {ev['name']}({ev['args']})\njarvis> ", end="", flush=True)
            elif ev["type"] == "error":
                print(f"\n  [error] {ev['message']}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(prog="jarvis")
    parser.add_argument("--doctor", action="store_true", help="check setup and exit")
    args = parser.parse_args()
    sys.exit(doctor() if args.doctor else chat_loop())


if __name__ == "__main__":
    main()
