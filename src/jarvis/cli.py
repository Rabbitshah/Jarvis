"""Terminal chat and a small doctor check."""
from __future__ import annotations

import argparse
import sys

from .agent import Agent
from .config import load_config
from .llm import LLMError, OllamaClient
from .memory.context import make_context_fn
from .memory.remember import Proposals
from .tools.builtin import build_registry


def doctor() -> int:
    cfg = load_config()
    llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)
    ok = True
    print(f"config model     : {cfg.model}")
    print(f"ollama url       : {cfg.ollama_url}")
    if llm.ping():
        print("ollama           : reachable")
        have = cfg.model in llm.list_models()
        print(f"model installed  : {'yes' if have else 'NO (run scripts/setup.sh)'}")
        ok &= have
        installed = any(m == cfg.embed_model or m.startswith(cfg.embed_model + ":") for m in llm.list_models())
        print(f"embed installed  : {'yes' if installed else f'NO (run: ollama pull {cfg.embed_model})'}")
        ok &= installed
        if installed:
            try:
                sizes = {len(v) for v in llm.embed(["hello", "a much longer second sentence", "hello"])}
                print(f"vector size      : {', '.join(map(str, sizes))} ({'constant' if len(sizes) == 1 else 'NOT constant'})")
                ok &= len(sizes) == 1
            except Exception as exc:  # noqa: BLE001
                print(f"vector size      : embedding failed ({exc})")
                ok = False
    else:
        print("ollama           : NOT reachable (run scripts/run.sh)")
        ok = False
    print(f"notes folder     : {cfg.notes_dir} ({'ok' if cfg.notes_dir.is_dir() else 'missing'})")
    print(f"tools            : {', '.join(build_registry(cfg).names())}")
    return 0 if ok else 1


def ingest_notes(full: bool = False) -> int:
    from .memory.ingest import ingest
    from .memory.store import StoreError

    cfg = load_config()
    llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)
    try:
        res = ingest(cfg, llm.embed, full=full)
    except (LLMError, StoreError) as exc:
        print(f"ingest failed: {exc}")
        return 1
    for name, n in res.files.items():
        print(f"  {n:>2} chunks  {name}")
    print(f"notes ingested   : {len(res.files)}  (skipped: {', '.join(res.skipped) or 'none'})")
    print(f"embedded now     : {res.embedded} chunks  (unchanged notes: {len(res.unchanged)}, "
          f"removed from index: {', '.join(res.removed) or 'none'})")
    print(f"chunks produced  : {res.chunks}")
    print(f"chunks in index  : {res.stored_total}  ({'match' if res.stored_total == res.chunks else 'MISMATCH'})")
    return 0 if res.stored_total == res.chunks else 1


def search_cmd(query: str, k: int) -> int:
    from .memory.search import search_notes
    from .memory.store import StoreError

    cfg = load_config()
    llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)
    try:
        hits = search_notes(cfg, llm.embed, query, k)
    except (LLMError, StoreError) as exc:
        print(f"search failed: {exc}")
        return 1
    for i, h in enumerate(hits, 1):
        snippet = " ".join(h.text.split())[:140]
        print(f"{i}. {h.score:.3f}  {h.file} (chunk {h.chunk})\n   {snippet}")
    return 0


def chat_loop() -> int:
    cfg = load_config()
    llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)
    proposals = Proposals(cfg, llm.embed)
    agent = Agent(llm, build_registry(cfg, llm.embed, proposals), cfg.system_prompt, cfg.max_tool_rounds,
                  cfg.max_history, make_context_fn(cfg, llm.embed), proposals)
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
        asked = []
        for ev in agent.chat(text):
            if ev["type"] == "token":
                print(ev["text"], end="", flush=True)
            elif ev["type"] == "sources":
                print(f"\n  [notes shown to the model] {', '.join(ev['files'])}\njarvis> ", end="", flush=True)
            elif ev["type"] == "tool_call":
                print(f"\n  [tool] {ev['name']}({ev['args']})\njarvis> ", end="", flush=True)
            elif ev["type"] == "confirm":
                asked.append(ev)
            elif ev["type"] == "error":
                print(f"\n  [error] {ev['message']}")
        print()
        for ev in asked:  # only a typed "y" from you saves anything
            if ev.get("from_context"):
                print("  ! Notes were shown to the model this turn. Save only if this fact really came from you.")
            try:
                answer = input(f"  Save to memory? \"{ev['fact']}\"  [y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = "n"
            print("  " + (proposals.approve(ev["id"]) if answer in ("y", "yes") else proposals.reject(ev["id"])))


def main() -> None:
    parser = argparse.ArgumentParser(prog="jarvis")
    parser.add_argument("--doctor", action="store_true", help="check setup and exit")
    parser.add_argument("--ingest", action="store_true", help="embed the notes into the index and exit")
    parser.add_argument("--full", action="store_true", help="with --ingest: embed every note again")
    parser.add_argument("--search", metavar="QUERY", help="search the note index and exit")
    parser.add_argument("-k", type=int, default=3, help="how many results for --search")
    args = parser.parse_args()
    if args.doctor:
        sys.exit(doctor())
    if args.ingest:
        sys.exit(ingest_notes(args.full))
    if args.search is not None:
        sys.exit(search_cmd(args.search, args.k))
    sys.exit(chat_loop())


if __name__ == "__main__":
    main()
