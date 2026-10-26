"""Speech to text with Whisper. Two backends so we can measure them side by side.

Both take 16 kHz mono float32 audio (a numpy array), so no ffmpeg is needed.
Heavy libraries are imported only when a backend is first used.
"""
import time
from pathlib import Path
from typing import Protocol

import numpy as np

from .recorder import SAMPLE_RATE, read_wav


class SttError(Exception):
    """Plain-text problem the user can act on."""


class Transcriber(Protocol):
    name: str

    def load(self) -> None: ...
    def transcribe(self, audio: np.ndarray) -> str: ...


def load_audio(path: Path) -> np.ndarray:
    """WAV file -> float32 in [-1, 1]. Only 16 kHz mono (what jarvis --record writes)."""
    try:
        data, rate = read_wav(path)
    except (OSError, EOFError) as exc:
        raise SttError(f"cannot read {path}: {exc}") from exc
    if rate != SAMPLE_RATE:
        raise SttError(f"{path} is {rate} Hz, expected {SAMPLE_RATE} Hz")
    return data.astype(np.float32) / 32768.0


class FasterWhisperStt:
    """faster-whisper (CTranslate2). On a Mac it runs on the CPU."""

    def __init__(self, model: str = "small", compute_type: str = "int8", language: str | None = "en"):
        self.name = f"faster-whisper:{model}"
        self.model_name, self.compute_type, self.language = model, compute_type, language
        self._model = None

    def load(self) -> None:
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(self.model_name, device="cpu", compute_type=self.compute_type)
        except Exception as exc:  # download or install problems come in many types
            raise SttError(f"cannot load {self.name}: {exc}") from exc

    def transcribe(self, audio: np.ndarray) -> str:
        self.load()
        segments, _info = self._model.transcribe(audio, language=self.language, beam_size=5)
        return " ".join(s.text.strip() for s in segments).strip()  # the generator does the work here


class MlxWhisperStt:
    """mlx-whisper (Apple GPU). Downloads the model from Hugging Face on first use."""

    def __init__(self, repo: str = "mlx-community/whisper-small-mlx", language: str | None = "en"):
        self.name = f"mlx-whisper:{repo.rsplit('/', 1)[-1]}"
        self.repo, self.language = repo, language
        self._mod = None

    def load(self) -> None:
        if self._mod is not None:
            return
        try:
            import mlx_whisper
            # a silent half-second clip makes the library fetch and load the model now
            mlx_whisper.transcribe(np.zeros(SAMPLE_RATE // 2, dtype=np.float32),
                                   path_or_hf_repo=self.repo, language=self.language)
            self._mod = mlx_whisper
        except Exception as exc:
            raise SttError(f"cannot load {self.name}: {exc}") from exc

    def transcribe(self, audio: np.ndarray) -> str:
        self.load()
        return self._mod.transcribe(audio, path_or_hf_repo=self.repo, language=self.language)["text"].strip()


def make(spec: str) -> Transcriber:
    """'faster:small' or 'mlx:mlx-community/whisper-small-mlx'."""
    kind, _, model = spec.partition(":")
    if kind == "faster" and model:
        return FasterWhisperStt(model)
    if kind == "mlx" and model:
        return MlxWhisperStt(model)
    raise SttError(f"unknown speech-to-text spec '{spec}' (use faster:<size> or mlx:<repo>)")


def timed(fn, *args):
    start = time.perf_counter()
    out = fn(*args)
    return out, time.perf_counter() - start
