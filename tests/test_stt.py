import sys
import types

import numpy as np
import pytest

from jarvis.voice import recorder, stt
from jarvis.voice.wer import word_error_rate


def test_wer():
    assert word_error_rate("What time is it", "what time is it?") == 0
    assert word_error_rate("what time is it", "what is it") == 0.25
    assert word_error_rate("a b", "x y z") == 1.5
    with pytest.raises(ValueError):
        word_error_rate("...", "x")


def test_load_audio_scales_and_checks_rate(tmp_path):
    recorder.write_wav(tmp_path / "a.wav", np.array([0, 16384, -32768], dtype=np.int16))
    audio = stt.load_audio(tmp_path / "a.wav")
    assert audio.dtype == np.float32 and list(audio) == [0.0, 0.5, -1.0]
    recorder.write_wav(tmp_path / "b.wav", np.zeros(10, dtype=np.int16), sample_rate=44100)
    with pytest.raises(stt.SttError, match="44100"):
        stt.load_audio(tmp_path / "b.wav")
    with pytest.raises(stt.SttError):
        stt.load_audio(tmp_path / "missing.wav")


def test_make():
    assert stt.make("faster:small").name == "faster-whisper:small"
    assert stt.make("mlx:mlx-community/whisper-base-mlx").name == "mlx-whisper:whisper-base-mlx"
    for bad in ("faster", "other:x", ""):
        with pytest.raises(stt.SttError):
            stt.make(bad)


def test_faster_whisper_backend(monkeypatch):
    seen = {}

    class Seg:
        def __init__(self, t):
            self.text = t

    class FakeModel:
        def __init__(self, name, device, compute_type):
            seen["init"] = (name, device, compute_type)

        def transcribe(self, audio, language, beam_size):
            seen["audio"] = audio
            return iter([Seg(" hello"), Seg("world ")]), None

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeModel))
    engine = stt.make("faster:small")
    audio = np.zeros(10, dtype=np.float32)
    assert engine.transcribe(audio) == "hello world"
    assert seen["init"] == ("small", "cpu", "int8") and seen["audio"] is audio


def test_mlx_backend(monkeypatch):
    calls = []

    def fake_transcribe(audio, path_or_hf_repo, language):
        calls.append((len(audio), path_or_hf_repo))
        return {"text": " hi there "}

    monkeypatch.setitem(sys.modules, "mlx_whisper", types.SimpleNamespace(transcribe=fake_transcribe))
    engine = stt.make("mlx:mlx-community/whisper-small-mlx")
    assert engine.transcribe(np.zeros(100, dtype=np.float32)) == "hi there"
    assert calls[0][0] == 8000 and calls[1] == (100, "mlx-community/whisper-small-mlx")  # warm-up, then real


def test_load_failure_is_plain_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "faster_whisper", None)  # import fails
    with pytest.raises(stt.SttError, match="cannot load"):
        stt.make("faster:small").load()


def test_config_has_stt_default_and_env_override(monkeypatch):
    from jarvis.config import load_config
    assert load_config().stt.startswith("mlx:")
    monkeypatch.setenv("JARVIS_STT", "faster:base")
    assert load_config().stt == "faster:base"
