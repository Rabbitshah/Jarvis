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
print(f"{'rank':<5} {'expected note':<38} question")
for case in cases:
    try:
        files = [h.file for h in search_notes(cfg, llm.embed, case["question"], k=3)]
    except (LLMError, StoreError) as exc:
        sys.exit(f"search failed: {exc}")
    rank = files.index(case["note"]) + 1 if case["note"] in files else None
    top1 += rank == 1
    top3 += rank is not None
    print(f"{rank or 'MISS':<5} {case['note']:<38} {case['question']}" + ("" if rank == 1 else f"   got: {', '.join(files)}"))
n = len(cases)
print(f"\ntop-1: {top1}/{n}   top-3: {top3}/{n}")
sys.exit(0 if top3 == n else 1)
