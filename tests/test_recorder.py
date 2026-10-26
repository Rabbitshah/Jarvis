import threading
import wave

import numpy as np
import pytest

from jarvis.voice import recorder
from jarvis.voice.recorder import Recording, RecorderError


class FakeStream:
    def __init__(self, callback, blocks):
        self.callback, self.blocks, self.closed = callback, blocks, False

    def start(self):
        for b in self.blocks:
            self.callback(b.reshape(-1, 1))  # sounddevice gives shape (frames, channels)

    def stop(self):
        pass

    def close(self):
        self.closed = True


def make_enter(n_calls=2):
    """First call returns at once (start); the second returns at once too (stop)."""
    return lambda: None


def run(tmp_path, blocks, **kw):
    holder = {}

    def opener(cb):
        holder["s"] = FakeStream(cb, blocks)
        return holder["s"]

    rec = recorder.record(tmp_path / "a.wav", make_enter(), open_stream=opener, say=lambda m: None, **kw)
    return rec, holder["s"]


def test_record_writes_playable_wav(tmp_path):
    audio = (np.sin(np.linspace(0, 100, 16000)) * 8000).astype(np.int16)
    rec, stream = run(tmp_path, [audio[:8000], audio[8000:]])
    assert stream.closed
    with wave.open(str(rec.path)) as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (1, 2, 16000)
        assert f.getnframes() == 16000
    data, rate = recorder.read_wav(rec.path)
    assert rate == 16000 and np.array_equal(data, audio)
    assert rec.seconds == pytest.approx(1.0) and rec.peak == int(np.abs(audio.astype(int)).max())
    assert recorder.advice(rec) is None


def test_silent_recording_gives_permission_hint(tmp_path):
    rec, _ = run(tmp_path, [np.zeros(1600, dtype=np.int16)])
    assert rec.silent and "microphone permission" in recorder.advice(rec)


def test_quiet_recording_gives_device_hint(tmp_path):
    rec, _ = run(tmp_path, [np.full(1600, 50, dtype=np.int16)])
    assert rec.quiet and "quiet" in recorder.advice(rec)


def test_nothing_recorded_is_an_error(tmp_path):
    with pytest.raises(RecorderError):
        run(tmp_path, [])


def test_max_seconds_stops_recording(tmp_path):
    release = threading.Event()
    calls = []

    def wait():  # start returns at once; stop never comes
        calls.append(1)
        if len(calls) > 1:
            release.wait(5)

    rec = recorder.record(tmp_path / "b.wav", wait, open_stream=lambda cb: FakeStream(cb, [np.ones(160, dtype=np.int16)]),
                          max_seconds=0.05, say=lambda m: None)
    release.set()
    assert rec.path.exists()


def test_play_without_afplay(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder.shutil, "which", lambda name: None)
    assert recorder.play(tmp_path / "x.wav") is False


def test_recording_properties():
    assert Recording(None, 1, 0).silent and Recording(None, 1, 10).quiet and not Recording(None, 1, 9000).quiet
