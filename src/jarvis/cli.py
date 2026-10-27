"""Terminal chat and a small doctor check."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .agent import Agent
from .config import ROOT, load_config
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
    from jarvis.voice.tts import PiperClient
    print(f"piper (optional) : {'reachable' if PiperClient(cfg.tts_url, cfg.tts_voice).ping() else 'not running (bash scripts/piper-up.sh)'}")
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


VOICE_PROMPT = ("\nYou are speaking out loud. Answer in at most two short sentences, in plain words. "
                "No lists, no symbols, no markdown.")


def build_agent(cfg, extra_prompt: str = ""):
    llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)
    proposals = Proposals(cfg, llm.embed)
    agent = Agent(llm, build_registry(cfg, llm.embed, proposals), cfg.system_prompt + extra_prompt, cfg.max_tool_rounds,
                  cfg.max_history, make_context_fn(cfg, llm.embed), proposals)
    return agent, proposals


def run_turn(agent, proposals, text: str, on_reply=None) -> str:
    """Send one message, print the answer as it streams, then ask y/N for any proposed memory.
    on_reply(text) runs once the answer is complete (voice mode speaks it). Returns the answer."""
    print("jarvis> ", end="", flush=True)
    asked, consulted, reply = [], [], ""
    for ev in agent.chat(text):
        if ev["type"] == "token":
            reply += ev["text"]
            print(ev["text"], end="", flush=True)
        elif ev["type"] == "sources":
            consulted = ev["files"]
        elif ev["type"] == "tool_call":
            print(f"\n  [tool] {ev['name']}({ev['args']})\njarvis> ", end="", flush=True)
        elif ev["type"] == "confirm":
            asked.append(ev)
        elif ev["type"] == "error":
            print(f"\n  [error] {ev['message']}")
    print()
    if consulted:
        print(f"  Notes consulted: {', '.join(consulted)}")
    if on_reply and reply.strip():
        on_reply(reply)
    for ev in asked:  # only a typed "y" from you saves anything
        if ev.get("from_context"):
            print("  ! Notes were shown to the model this turn. Save only if this fact really came from you.")
        try:
            answer = input(f"  Save to memory? \"{ev['fact']}\"  [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "n"
        print("  " + (proposals.approve(ev["id"]) if answer in ("y", "yes") else proposals.reject(ev["id"])))
    return reply


def chat_loop() -> int:
    cfg = load_config()
    agent, proposals = build_agent(cfg)
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
        run_turn(agent, proposals, text)


def make_speaker(cfg):
    """Returns speak(text), or None if Piper is not running (replies then stay text only)."""
    from jarvis.voice import tts

    piper = tts.PiperClient(cfg.tts_url, cfg.tts_voice)
    if not piper.ping():
        print("Piper is not running, so replies will be text only. Start it with: bash scripts/piper-up.sh")
        return None
    out = ROOT / ".tools" / "recordings" / "reply.wav"  # overwritten each time, never committed

    def speak(text: str) -> None:
        words = tts.speakable(text)
        if not words:
            return
        try:
            start = time.perf_counter()
            wav = piper.synthesize(words)
            took = time.perf_counter() - start
        except tts.TtsError as exc:
            print(f"  [voice] {exc}")
            return
        print(f"  (voice ready after {took:.2f} s)")
        if not tts.play_wav_bytes(wav, out):
            print("  [voice] afplay not found, cannot play audio")

    return speak


def say_cmd(text: str) -> int:
    speak = make_speaker(load_config())
    if speak is None:
        return 1
    speak(text)
    return 0


def voice_loop(speak_replies: bool = True) -> int:
    """Speak a question (Enter, talk, Enter); Jarvis answers in text and out loud. Typed text also works."""
    from jarvis.voice import stt
    from jarvis.voice.listen import listen

    cfg = load_config()
    try:
        engine = stt.make(cfg.stt)
        print(f"Loading speech model {engine.name} ...")
        _, load_s = stt.timed(engine.load)
    except stt.SttError as exc:
        print(f"error: {exc}")
        return 1
    print(f"Speech model ready in {load_s:.1f} s.")
    agent, proposals = build_agent(cfg, VOICE_PROMPT)
    speak = make_speaker(cfg) if speak_replies else None
    wav = ROOT / ".tools" / "recordings" / "last.wav"  # overwritten each time, never committed
    print(f"Jarvis voice ({cfg.model}). Press Enter to talk. Type text to type instead. /reset, /exit.")
    while True:
        try:
            line = input("\nvoice> (Enter = talk) ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if line == "/exit":
            return 0
        if line == "/reset":
            agent.reset()
            print("history cleared")
            continue
        try:
            text = line or listen(engine, wav, wait_for_enter=input, already_started=True)
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not text:
            continue
        if not line:
            print(f"you said> {text}")
        run_turn(agent, proposals, text, on_reply=speak)


def main() -> None:
    parser = argparse.ArgumentParser(prog="jarvis")
    parser.add_argument("--doctor", action="store_true", help="check setup and exit")
    parser.add_argument("--ingest", action="store_true", help="embed the notes into the index and exit")
    parser.add_argument("--full", action="store_true", help="with --ingest: embed every note again")
    parser.add_argument("--search", metavar="QUERY", help="search the note index and exit")
    parser.add_argument("-k", type=int, default=3, help="how many results for --search")
    parser.add_argument("--record", metavar="WAV", help="record the microphone to a WAV file, play it back, exit")
    parser.add_argument("--transcribe", metavar="WAV", help="turn a WAV file into text with the configured Whisper, exit")
    parser.add_argument("--voice", action="store_true", help="talk to Jarvis: speak, get a text answer")
    parser.add_argument("--no-speak", action="store_true", help="with --voice: do not read replies out loud")
    parser.add_argument("--say", metavar="TEXT", help="speak TEXT with Piper and exit")
    parser.add_argument("--devices", action="store_true", help="list microphones and exit")
    args = parser.parse_args()
    if args.voice:
        sys.exit(voice_loop(not args.no_speak))
    if args.say:
        sys.exit(say_cmd(args.say))
    if args.transcribe:
        sys.exit(transcribe_cmd(args.transcribe))
    if args.devices:
        sys.exit(devices_cmd())
    if args.record:
        sys.exit(record_cmd(args.record))
    if args.doctor:
        sys.exit(doctor())
    if args.ingest:
        sys.exit(ingest_notes(args.full))
    if args.search is not None:
        sys.exit(search_cmd(args.search, args.k))
    sys.exit(chat_loop())


if __name__ == "__main__":
    main()
