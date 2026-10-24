"""Run the search test cases in notes/eval-cases.toml against the real index.

Each case: a question and the one note that should answer it. Prints where it ranked.
Pass = the right note is in the top 3. Exit code 1 if any case fails.
Run: bash scripts/search-eval.sh
"""
import sys
import tomllib

from jarvis.config import load_config
from jarvis.llm import LLMError, OllamaClient
from jarvis.memory.search import search_notes
from jarvis.memory.store import StoreError

cfg = load_config()
path = cfg.notes_dir / "eval-cases.toml"
if not path.is_file():
    sys.exit(f"missing {path}")
cases = tomllib.loads(path.read_text(encoding="utf-8"))["case"]
llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)

top1 = top3 = 0
relevant: list[float] = []
print(f"{'rank':<5} {'expected note':<38} question")
for case in cases:
    try:
        hits = search_notes(cfg, llm.embed, case["question"], k=3)
        files = [h.file for h in hits]
    except (LLMError, StoreError) as exc:
        sys.exit(f"search failed: {exc}")
    rank = files.index(case["note"]) + 1 if case["note"] in files else None
    right = [h.score for h in hits if h.file == case["note"]]
    if right:
        relevant.append(max(right))
    top1 += rank == 1
    top3 += rank is not None
    print(f"{rank or 'MISS':<5} {case['note']:<38} {case['question']}" + ("" if rank == 1 else f"   got: {', '.join(files)}"))
n = len(cases)
print(f"\ntop-1: {top1}/{n}   top-3: {top3}/{n}")

# Calibration for [memory] min_score: questions that no note should answer.
off = []
for q in tomllib.loads(path.read_text(encoding="utf-8")).get("offtopic", {}).get("questions", []):
    top = search_notes(cfg, llm.embed, q, k=1)[0]
    off.append(top.score)
    print(f"off-topic {top.score:.3f}  {q}   (nearest: {top.file})")
if relevant:
    print(f"\nscore of the right note: lowest {min(relevant):.3f}, highest {max(relevant):.3f}")
if off and relevant:
    print(f"highest off-topic score: {max(off):.3f}   -> min_score should sit between {max(off):.3f} and {min(relevant):.3f}"
          f" (now {cfg.memory_min_score})")
sys.exit(0 if top3 == n else 1)
