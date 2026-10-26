"""Compare Whisper backends on your own recordings. Writes docs/STT.md.

Clips: .tools/recordings/*.wav. Put what you said in a .txt next to each clip
(clip1.wav + clip1.txt) to get the word error rate.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from jarvis.voice import stt  # noqa: E402
from jarvis.voice.wer import word_error_rate  # noqa: E402

DEFAULT_SPECS = [
    "faster:base",
    "faster:small",
    "mlx:mlx-community/whisper-base-mlx",
    "mlx:mlx-community/whisper-small-mlx",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", default=str(ROOT / ".tools" / "recordings"))
    ap.add_argument("--spec", action="append", help="faster:<size> or mlx:<repo>; repeat for more")
    args = ap.parse_args()
    clips = sorted(Path(args.clips).glob("*.wav"))
    if not clips:
        print(f"no .wav clips in {args.clips}. Record some with scripts/record.sh <file>")
        return 1
    audio = {c: stt.load_audio(c) for c in clips}
    rows, texts = [], []
    for spec in args.spec or DEFAULT_SPECS:
        engine = stt.make(spec)
        print(f"== {engine.name}")
        try:
            _, load_s = stt.timed(engine.load)
        except stt.SttError as exc:
            print(f"   SKIPPED: {exc}")
            rows.append((engine.name, "-", "-", "-", f"failed: {str(exc)[:80]}"))
            continue
        wers, rtfs, warm = [], [], []
        for clip in clips:
            seconds = len(audio[clip]) / stt.SAMPLE_RATE
            engine.transcribe(audio[clip])                      # first run warms up, not counted
            text, took = stt.timed(engine.transcribe, audio[clip])
            warm.append(took)
            rtfs.append(took / seconds)
            ref = clip.with_suffix(".txt")
            wer = word_error_rate(ref.read_text(), text) if ref.exists() else None
            if wer is not None:
                wers.append(wer)
            texts.append((engine.name, clip.name, text, wer))
            print(f"   {clip.name}: {took:.2f}s ({took / seconds:.2f}x real time) wer={wer}  {text!r}")
        rows.append((engine.name, f"{load_s:.1f}", f"{sum(warm) / len(warm):.2f}",
                     f"{sum(rtfs) / len(rtfs):.2f}", f"{sum(wers) / len(wers):.3f}" if wers else "no .txt"))
    out = ["# Speech-to-text comparison", "",
           f"{len(clips)} clips from your microphone. Time = warm run, average per clip. "
           "Real-time factor 0.10 means 1 s of speech takes 0.1 s. WER = share of words wrong (lower is better).", "",
           "| Engine | Load (s) | Time per clip (s) | Real-time factor | WER |", "| --- | --- | --- | --- | --- |"]
    out += [f"| {' | '.join(r)} |" for r in rows]
    out += ["", "## What each engine heard", "", "| Engine | Clip | Text | WER |", "| --- | --- | --- | --- |"]
    out += [f"| {e} | {c} | {t.replace('|', '/')} | {'' if w is None else f'{w:.2f}'} |" for e, c, t, w in texts]
    (ROOT / "docs" / "STT.md").write_text("\n".join(out) + "\n")
    print("\nwrote docs/STT.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
