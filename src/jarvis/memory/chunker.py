"""Split a note into chunks small enough to embed well, keeping paragraphs whole."""
from __future__ import annotations

import re

DEFAULT_MAX_CHARS = 800


def _split_long(text: str, max_chars: int) -> list[str]:
    """Break one oversized paragraph on sentence ends, then hard-cut what is still too long."""
    out, cur = [], ""
    for sent in re.split(r"(?<=[.!?])\s+", text):
        while len(sent) > max_chars:
            if cur:
                out.append(cur)
                cur = ""
            out.append(sent[:max_chars])
            sent = sent[max_chars:]
        if cur and len(cur) + 1 + len(sent) > max_chars:
            out.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        out.append(cur)
    return out


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    """Paragraphs are packed together up to max_chars. A heading stays with the text after it."""
    if max_chars < 50:
        raise ValueError("max_chars must be at least 50")
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if p.strip()]
    glued: list[str] = []
    pending = ""  # a heading line waits here and joins the paragraph after it
    for p in paras:
        if "\n" not in p and p.startswith("#"):
            pending = f"{pending}\n\n{p}".strip()
            continue
        glued.append(f"{pending}\n\n{p}".strip() if pending else p)
        pending = ""
    if pending:
        glued.append(pending)
    pieces: list[str] = []
    for p in glued:
        pieces.extend([p] if len(p) <= max_chars else _split_long(p, max_chars))
    chunks: list[str] = []
    cur = ""
    for piece in pieces:
        joined = f"{cur}\n\n{piece}" if cur else piece
        if cur and len(joined) > max_chars:
            chunks.append(cur)
            cur = piece
        else:
            cur = joined
    if cur:
        chunks.append(cur)
    return [c for c in chunks if c.strip()]
