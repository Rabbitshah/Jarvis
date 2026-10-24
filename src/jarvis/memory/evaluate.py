"""Score search quality: for each test question, where does the right note rank?"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from ..config import Config
from .search import Embed, search_notes

DEPTH = 5  # how far down the results to look


@dataclass(frozen=True)
class CaseResult:
    question: str
    wanted: list[str]
    files: list[str]       # results in order (best first)
    scores: list[float]
    rank: int | None       # 1-based position of the best right note, None = not in the top DEPTH


@dataclass(frozen=True)
class Scores:
    n: int
    top1: int
    hit3: int
    hit5: int
    mrr: float  # average of 1/rank (1 for rank 1, 0.5 for rank 2, 0 for a miss)


def load_cases(path: Path) -> tuple[list[dict], list[str]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return data["case"], data.get("offtopic", {}).get("questions", [])


def run_cases(cfg: Config, embed: Embed, cases: list[dict]) -> list[CaseResult]:
    out = []
    for case in cases:
        wanted = case["note"] if isinstance(case["note"], list) else [case["note"]]
        hits = search_notes(cfg, embed, case["question"], k=DEPTH)
        files = [h.file for h in hits]
        ranks = [files.index(w) + 1 for w in wanted if w in files]
        out.append(CaseResult(case["question"], wanted, files, [h.score for h in hits], min(ranks) if ranks else None))
    return out


def summarize(results: list[CaseResult]) -> Scores:
    n = len(results)
    rk = [r.rank for r in results]
    return Scores(
        n=n,
        top1=sum(r == 1 for r in rk),
        hit3=sum(r is not None and r <= 3 for r in rk),
        hit5=sum(r is not None for r in rk),
        mrr=sum(1 / r for r in rk if r) / n if n else 0.0,
    )
