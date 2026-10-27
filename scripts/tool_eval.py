"""Score a model on the questions Jarvis must get right. Writes docs/TOOLEVAL-<model>.md and prints a table.

  scripts/tool-eval.sh llama3.1:8b          (3 trials per question)
  scripts/tool-eval.sh qwen2.5:7b --trials 5
"""
import argparse
import dataclasses
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from jarvis import toolcheck  # noqa: E402
from jarvis.cli import VOICE_PROMPT, build_agent  # noqa: E402
from jarvis.config import load_config  # noqa: E402
from jarvis.memory.evaluate import load_cases  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--trials", type=int, default=3)
    args = ap.parse_args()
    cfg = dataclasses.replace(load_config(), model=args.model)
    cases = toolcheck.builtin_cases(datetime.now().astimezone())
    cases_file = ROOT / "notes" / "eval-cases.toml"
    if cases_file.exists():
        cases += toolcheck.notes_cases(load_cases(cases_file)[0])
    rows, failures, total_ok, total, total_ans = [], [], 0, 0, 0
    for case in cases:
        results = []
        for _ in range(args.trials):
            now = datetime.now().astimezone()
            if case.name in ("time", "date"):  # the clock moves between trials
                case = toolcheck.builtin_cases(now)[0 if case.name == "time" else 1]
            out = toolcheck.run_case(lambda: build_agent(cfg, VOICE_PROMPT)[0], case, time.perf_counter)
            results.append(out)
            if not out.ok:
                failures.append(f"- **{case.name}** ({out.problem}): `{out.answer[:160]!r}`")
        ok = sum(r.ok for r in results)
        ans = sum(r.answer_ok for r in results)
        total_ans += ans
        total_ok += ok
        total += len(results)
        avg = sum(r.seconds for r in results) / len(results)
        rows.append(f"| {case.name} | {ans}/{len(results)} | {ok}/{len(results)} | {avg:.1f} |")
        print(f"{case.name:45s} answer {ans}/{len(results)}  strict {ok}/{len(results)}  {avg:.1f}s", flush=True)
    text = [f"# Tool-use check: {args.model}" + ("" if cfg.memory_auto_context else " (automatic note search OFF)"), "",
            f"Answer correct: {total_ans}/{total} ({100 * total_ans / total:.0f}%). Strict (answer correct AND the right tools "
            f"used, e.g. no notes search for a general question): {total_ok}/{total} ({100 * total_ok / total:.0f}%). "
            f"{args.trials} trials per question, same agent and prompt as voice mode. Notes questions pass when the right note was consulted.", "",
            "| Question | Answer correct | Strict | Avg seconds |", "| --- | --- | --- | --- |", *rows, "", "## Failures", "", *(failures or ["none"])]
    safe = args.model.replace(":", "-").replace("/", "-") + ("" if cfg.memory_auto_context else "-no-auto-context")
    (ROOT / "docs" / f"TOOLEVAL-{safe}.md").write_text("\n".join(text) + "\n")
    print(f"\n{args.model}: answer correct {total_ans}/{total}, strict {total_ok}/{total}. wrote docs/TOOLEVAL-{safe}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
