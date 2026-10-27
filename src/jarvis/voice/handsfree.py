"""Always-listening loop pieces: a stream of 80 ms frames, waiting for the wake word, capturing one request."""
import queue
import select
import sys
from typing import Callable, Optional, Protocol

import numpy as np

from . import recorder
from .endpoint import Endpointer, NoiseTracker
from .wake import FRAME, WakeWord


class Frames(Protocol):
    def get(self, timeout: float = 0.5) -> Optional[np.ndarray]: ...
    def flush(self) -> None: ...


class MicFrames:
    """80 ms frames from the microphone. Used as `with MicFrames() as frames:`."""

    def __init__(self, open_stream: Callable = recorder.open_microphone):
        self._open = open_stream
        self._q: queue.Queue = queue.Queue(maxsize=600)  # 48 s; older audio is dropped, not kept
        self._stream = None

    def _on_audio(self, indata) -> None:
        try:
            self._q.put_nowait(np.array(indata, dtype=np.int16).reshape(-1))
        except queue.Full:
            pass

    def __enter__(self) -> "MicFrames":
        self._stream = self._open(self._on_audio, FRAME) if self._open is recorder.open_microphone else self._open(self._on_audio)
        self._stream.start()
        return self

    def __exit__(self, *exc) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()

    def get(self, timeout: float = 0.5) -> Optional[np.ndarray]:
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None

    def flush(self) -> None:
        while True:
            try:
                self._q.get_nowait()
            except queue.Empty:
                return


def enter_pressed() -> bool:
    """True if Enter was pressed in the terminal (push-to-talk still works in hands-free mode)."""
    try:
        ready, _, _ = select.select([sys.stdin], [], [], 0)
    except (OSError, ValueError):
        return False
    if ready:
        sys.stdin.readline()
        return True
    return False


def wait_for_wake(frames: Frames, wake: WakeWord, noise: NoiseTracker,
                  pressed: Callable[[], bool] = enter_pressed,
                  on_near: Optional[Callable[[float], None]] = None, near: float = 0.25) -> str:
    """Block until 'Hey Jarvis' ('wake') or Enter ('enter'). Audio before that is never stored.
    on_near(score) is called (at most once a second) when the model half-heard it."""
    wake.reset()  # the pause after the last detection must not eat the next 'Hey Jarvis'
    quiet_frames = 0
    while True:
        if pressed():
            return "enter"
        frame = frames.get()
        if frame is None or frame.size != FRAME:
            continue
        if wake.process(frame):
            return "wake"
        quiet_frames += 1
        if on_near and near <= wake.last_score < wake.threshold and quiet_frames >= 12:
            quiet_frames = 0
            on_near(wake.last_score)
        noise.add(frame)


def capture_utterance(frames: Frames, noise: NoiseTracker, **endpoint_options) -> tuple[Optional[np.ndarray], str]:
    """Record until you stop speaking. Returns (audio or None, why it stopped)."""
    end = Endpointer(noise.level, **endpoint_options)
    blocks: list[np.ndarray] = []
    while True:
        frame = frames.get()
        if frame is None:
            continue
        blocks.append(frame)
        reason = end.feed(frame)
        if reason:
            audio = np.concatenate(blocks)
            return (audio if end.speech_seen else None), reason
