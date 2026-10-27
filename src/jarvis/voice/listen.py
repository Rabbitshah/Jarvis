"""One spoken question: record, check the recording, turn it into text."""
import re
from pathlib import Path
from typing import Callable

from . import recorder, stt


WAKE = re.compile(r"^\s*(?:(?:hey|hi|hello|ok|okay)[\s,]+)?jarvis\b[\s,.:!?-]*", re.IGNORECASE)


def strip_wake_phrase(text: str) -> str:
    """'Hey Jarvis, what time is it?' -> 'what time is it?'. The name would otherwise pull the
    Jarvis project notes into every question (Day 25: it confused a plain time question)."""
    return WAKE.sub("", text, count=1).strip()


def listen(engine: stt.Transcriber, wav_path: Path, wait_for_enter: Callable[[], None],
           open_stream: Callable = recorder.open_microphone, say: Callable[[str], None] = print,
           already_started: bool = False) -> str | None:
    """Returns the text, or None if nothing usable was heard (the reason is passed to say)."""
    try:
        rec = recorder.record(wav_path, wait_for_enter, open_stream=open_stream, say=say,
                              already_started=already_started)
    except recorder.RecorderError as exc:
        say(f"error: {exc}")
        return None
    hint = recorder.advice(rec)
    if hint:  # silent or very quiet: Whisper makes up words from silence, so do not send it
        say(f"! {hint}")
        return None
    try:
        text, took = stt.timed(engine.transcribe, stt.load_audio(rec.path))
    except stt.SttError as exc:
        say(f"error: {exc}")
        return None
    heard = text.strip()
    if not heard:
        say("Could not hear any words. Try again.")
        return None
    text = strip_wake_phrase(heard)
    if not text:
        say("I only heard my name. Say the question after it.")
        return None
    say(f"  ({rec.seconds:.1f} s of audio, transcribed in {took:.2f} s)")
    return text
