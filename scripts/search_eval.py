"""Run the search test cases in notes/eval-cases.toml against the real index.

Each case: a question and the note that should answer it (or a list: any of them counts).
Prints where it ranked. Pass = a right note is in the top 3. Exit code 1 if any case fails.
Run: bash scripts/search-eval.sh
"""
import sys

from jarvis.config import load_config
from jarvis.llm import LLMError, OllamaClient
from jarvis.memory.evaluate import load_cases, run_cases, summarize
from jarvis.memory.search import search_notes
from jarvis.memory.store import StoreError

cfg = load_config()
path = cfg.notes_dir / "eval-cases.toml"
if not path.is_file():
    sys.exit(f"missing {path}")
cases, offtopic = load_cases(path)
llm = OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)

try:
    results = run_cases(cfg, llm.embed, cases)
    off = [(q, search_notes(cfg, llm.embed, q, k=1)[0]) for q in offtopic]
except (LLMError, StoreError) as exc:
    sys.exit(f"search failed: {exc}")

print(f"{'rank':<5} {'expected note':<38} question")
for r in results:
    rank = r.rank if r.rank and r.rank <= 3 else "MISS"
    note = f"   got: {', '.join(r.files[:3])}" if r.rank != 1 else ""
    print(f"{rank!s:<5} {'|'.join(r.wanted):<38} {r.question}{note}")
s = summarize(results)
print(f"\ntop-1: {s.top1}/{s.n}   top-3 (hit@3): {s.hit3}/{s.n}   top-5: {s.hit5}/{s.n}   MRR: {s.mrr:.3f}")

relevant = [sc for r in results for f, sc in zip(r.files, r.scores) if f in r.wanted]
for q, top in off:
    print(f"off-topic {top.score:.3f}  {q}   (nearest: {top.file})")
if relevant:
    print(f"\nscore of the right note: lowest {min(relevant):.3f}, highest {max(relevant):.3f}")
if off and relevant:
    hi = max(t.score for _q, t in off)
    print(f"highest off-topic score: {hi:.3f}   -> min_score should sit between {hi:.3f} and {min(relevant):.3f}"
          f" (now {cfg.memory_min_score})")
sys.exit(0 if s.hit3 == s.n else 1)
