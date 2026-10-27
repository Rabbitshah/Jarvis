import numpy as np

from jarvis.voice import recorder
from jarvis.voice.listen import listen


class FakeStream:
    def __init__(self, cb, audio):
        self.cb, self.audio = cb, audio

    def start(self):
        self.cb(self.audio.reshape(-1, 1))

    def stop(self): pass
    def close(self): pass


class FakeEngine:
    name = "fake"

    def __init__(self, text):
        self.text, self.heard = text, None

    def transcribe(self, audio):
        self.heard = audio
        return self.text


def run(tmp_path, audio, text="  what time is it ", **kw):
    said, engine = [], FakeEngine(text)
    out = listen(engine, tmp_path / "x.wav", lambda: None, open_stream=lambda cb: FakeStream(cb, audio),
                 say=said.append, already_started=True, **kw)
    return out, said, engine


def tone(n=16000, level=8000):
    return (np.sin(np.linspace(0, 200, n)) * level).astype(np.int16)


def test_good_recording_returns_text(tmp_path):
    out, said, engine = run(tmp_path, tone())
    assert out == "what time is it" and engine.heard.dtype == np.float32
    assert "Press Enter" not in " ".join(said)  # start prompt skipped


def test_silent_recording_never_reaches_whisper(tmp_path):
    out, said, engine = run(tmp_path, np.zeros(1600, dtype=np.int16))
    assert out is None and engine.heard is None and any("microphone permission" in m for m in said)


def test_quiet_recording_never_reaches_whisper(tmp_path):
    out, said, engine = run(tmp_path, tone(level=40))
    assert out is None and engine.heard is None


def test_empty_transcript(tmp_path):
    out, said, _ = run(tmp_path, tone(), text="   ")
    assert out is None and any("Could not hear" in m for m in said)


def test_recorder_error_is_said(tmp_path):
    def broken(cb):
        raise recorder.RecorderError("no mic")
    said = []
    assert listen(FakeEngine("x"), tmp_path / "x.wav", lambda: None, open_stream=broken,
                  say=said.append, already_started=True) is None
    assert said == ["error: no mic"]


def test_wake_phrase_is_removed(tmp_path):
    from jarvis.voice.listen import strip_wake_phrase
    assert strip_wake_phrase("Hey Jarvis, what time is it?") == "what time is it?"
    assert strip_wake_phrase("jarvis what is my plan for grad school") == "what is my plan for grad school"
    assert strip_wake_phrase("Okay Jarvis: remind me") == "remind me"
    assert strip_wake_phrase("Tell Jarvis to wait") == "Tell Jarvis to wait"  # only at the start
    assert strip_wake_phrase("Jarvisfoo bar") == "Jarvisfoo bar"
    assert strip_wake_phrase("Hey Jarvis.") == ""
    out, _, _ = run(tmp_path, tone(), text="Hey Jarvis, what time is it?")
    assert out == "what time is it?"
    out, said, _ = run(tmp_path, tone(), text="Hey Jarvis")
    assert out is None and any("only heard my name" in m for m in said)
