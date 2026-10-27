"""Decide when you have finished speaking, by loudness (no extra model)."""
from collections import deque
from typing import Optional

import numpy as np

FRAME_S = 0.08


def rms(frame: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(frame.astype(np.float64))))) if frame.size else 0.0


class NoiseTracker:
    """Typical loudness of the room while nobody speaks: the median of the last few seconds."""

    def __init__(self, seconds: float = 4.0):
        self._values: deque[float] = deque(maxlen=int(seconds / FRAME_S))

    def add(self, frame: np.ndarray) -> None:
        self._values.append(rms(frame))

    @property
    def level(self) -> float:
        return float(np.median(self._values)) if self._values else 0.0


class Endpointer:
    """feed() each 80 ms frame after the wake word. Returns None to keep going, or why it stopped:
    'done' (you spoke, then paused), 'no_speech' (nothing heard in time), 'max' (too long)."""

    def __init__(self, noise_level: float, min_rms: float = 400.0, speech_factor: float = 3.0,
                 end_silence_s: float = 1.0, start_timeout_s: float = 6.0, max_s: float = 15.0,
                 ignore_first_s: float = 0.3):
        self.threshold = max(min_rms, noise_level * speech_factor)
        self.end_silence_s, self.start_timeout_s, self.max_s, self.ignore_first_s = (
            end_silence_s, start_timeout_s, max_s, ignore_first_s)
        self.elapsed = 0.0
        self.silent_for = 0.0
        self.speech_seen = False

    def feed(self, frame: np.ndarray) -> Optional[str]:
        self.elapsed += FRAME_S
        if self.elapsed <= self.ignore_first_s:  # the 'ding' that says Jarvis is listening
            return None
        if rms(frame) >= self.threshold:
            self.speech_seen, self.silent_for = True, 0.0
        else:
            self.silent_for += FRAME_S
        if self.speech_seen and self.silent_for >= self.end_silence_s:
            return "done"
        if not self.speech_seen and self.elapsed >= self.start_timeout_s:
            return "no_speech"
        if self.elapsed >= self.max_s:
            return "max"
        return None
