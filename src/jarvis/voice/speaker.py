"""Speak an answer while it is still being written.

Sentences are cut from the token stream as they finish. One thread turns each sentence into audio
(Piper) while another plays the one before it, so the first sentence is heard long before the
last one exists. The voice and the player are injected, so tests need no audio.
"""
import queue
import re
import threading
import time
from typing import Callable

from . import tts

# at least 12 characters, then . ! ? followed by whitespace, or a line break (so "Dr. X" and "3.5" do not split)
SENTENCE = re.compile(r"(.{12,}?(?:[.!?]\s+|\n+))", re.DOTALL)


class StreamingSpeaker:
    def __init__(self, synth: Callable[[str], bytes], play: Callable[[bytes], None],
                 stop_playing: Callable[[], None] = lambda: None, limit: int = tts.MAX_SPOKEN_CHARS,
                 say: Callable[[str], None] = print):
        self._synth, self._play, self._stop_playing, self._limit, self._say = synth, play, stop_playing, limit, say
        self.reset()

    def reset(self) -> None:
        self._buf = ""
        self._spoken_chars = 0
        self._failed = False
        self._stopped = False
        self.sentences: list[str] = []
        self.first_sound_at: float | None = None
        self._q_text: queue.Queue = queue.Queue()
        self._q_audio: queue.Queue = queue.Queue()
        self._threads = [threading.Thread(target=self._synth_loop, daemon=True),
                         threading.Thread(target=self._play_loop, daemon=True)]
        for t in self._threads:
            t.start()

    # --- called from the main thread -------------------------------------------------
    def feed(self, text: str) -> None:
        self._buf += text
        while (m := SENTENCE.match(self._buf)):
            self._enqueue(m.group(1))
            self._buf = self._buf[m.end():]

    def finish(self) -> None:
        """Send what is left, then wait until everything has been said."""
        if self._buf.strip():
            self._enqueue(self._buf)
        self._buf = ""
        self._q_text.put(None)
        for t in self._threads:
            t.join()

    def stop(self) -> None:
        self._stopped = True
        self._stop_playing()
        self._q_text.put(None)

    # --- internals ---------------------------------------------------------------------
    def _enqueue(self, sentence: str) -> None:
        clean = tts.speakable(sentence, limit=10**6)
        if not clean or self._spoken_chars >= self._limit:
            return  # long answers are shown, not read out in full
        self._spoken_chars += len(clean)
        self.sentences.append(clean)
        self._q_text.put(clean)

    def _synth_loop(self) -> None:
        for sentence in iter(self._q_text.get, None):
            if self._stopped:
                continue
            try:
                self._q_audio.put(self._synth(sentence))
            except tts.TtsError as exc:
                if not self._failed:
                    self._failed = True
                    self._say(f"  [voice] {exc}")
        self._q_audio.put(None)

    def _play_loop(self) -> None:
        for wav in iter(self._q_audio.get, None):
            if self._stopped:
                continue
            if self.first_sound_at is None:
                self.first_sound_at = time.perf_counter()
            self._play(wav)
