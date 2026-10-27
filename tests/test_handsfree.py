import numpy as np

from jarvis.voice.endpoint import FRAME_S, Endpointer, NoiseTracker, rms
from jarvis.voice.handsfree import capture_utterance, wait_for_wake
from jarvis.voice.wake import FRAME, WakeWord


def frame(level: int) -> np.ndarray:
    return np.full(FRAME, level, dtype=np.int16)


class FakeFrames:
    def __init__(self, frames):
        self.frames = list(frames)

    def get(self, timeout=0.5):
        return self.frames.pop(0) if self.frames else frame(0)

    def flush(self):
        self.frames.clear()


def test_wake_fires_once_then_cools_down():
    scores = iter([0.1, 0.9, 0.9, 0.9, 0.1])
    ww = WakeWord(lambda f: next(scores), threshold=0.5, cooldown_frames=3)
    assert [ww.process(frame(0)) for _ in range(5)] == [False, True, False, False, False]
    assert ww.last_score == 0.1


def test_wake_below_threshold_never_fires():
    ww = WakeWord(lambda f: 0.49, threshold=0.5)
    assert not any(ww.process(frame(0)) for _ in range(50))


def test_noise_tracker_uses_median():
    n = NoiseTracker(seconds=1.0)
    for level in (100, 100, 100, 5000):
        n.add(frame(level))
    assert n.level == 100
    assert rms(frame(300)) == 300


def test_endpointer_done_after_speech_then_silence():
    e = Endpointer(noise_level=50, end_silence_s=0.4, ignore_first_s=0.0)
    out = [e.feed(frame(3000)) for _ in range(5)] + [e.feed(frame(0)) for _ in range(6)]
    assert out[:5] == [None] * 5 and "done" in out and e.speech_seen


def test_endpointer_no_speech_and_max():
    e = Endpointer(noise_level=50, start_timeout_s=0.8, ignore_first_s=0.0)
    assert [r for r in (e.feed(frame(10)) for _ in range(20)) if r][0] == "no_speech"
    e = Endpointer(noise_level=50, max_s=0.8, ignore_first_s=0.0)
    assert [r for r in (e.feed(frame(3000)) for _ in range(20)) if r][0] == "max"


def test_endpointer_threshold_follows_noisy_room():
    assert Endpointer(noise_level=1000).threshold == 3000
    assert Endpointer(noise_level=10).threshold == 400
    assert FRAME_S == 0.08


def test_wait_for_wake_by_phrase_and_by_enter():
    ww = WakeWord(lambda f: 0.9 if f[0] == 7 else 0.0, threshold=0.5)
    frames = FakeFrames([frame(0), frame(0), frame(7)])
    assert wait_for_wake(frames, ww, NoiseTracker(), pressed=lambda: False) == "wake"
    assert wait_for_wake(FakeFrames([]), ww, NoiseTracker(), pressed=lambda: True) == "enter"


def test_wait_for_wake_ignores_wrong_sized_frames():
    ww = WakeWord(lambda f: 0.9, threshold=0.5)
    frames = FakeFrames([np.zeros(10, dtype=np.int16), frame(1)])
    assert wait_for_wake(frames, ww, NoiseTracker(), pressed=lambda: False) == "wake"


def test_capture_utterance_returns_audio_when_speech_heard():
    frames = FakeFrames([frame(3000)] * 4 + [frame(0)] * 20)
    audio, why = capture_utterance(frames, NoiseTracker(), ignore_first_s=0.0, end_silence_s=0.4)
    assert why == "done" and audio is not None and audio.size > 4 * FRAME


def test_capture_utterance_none_when_silent():
    audio, why = capture_utterance(FakeFrames([]), NoiseTracker(), ignore_first_s=0.0, start_timeout_s=0.8)
    assert audio is None and why == "no_speech"


def test_cooldown_does_not_eat_next_wake_after_capture():
    ww = WakeWord(lambda f: 0.9, threshold=0.5, cooldown_frames=25)
    assert ww.process(frame(0))            # first detection starts the pause
    assert not ww.process(frame(0))        # still paused
    assert wait_for_wake(FakeFrames([frame(1)]), ww, NoiseTracker(), pressed=lambda: False) == "wake"


def test_near_miss_is_reported():
    seen = []
    scores = iter([0.3] * 12 + [0.9])
    ww = WakeWord(lambda f: next(scores), threshold=0.5)
    wait_for_wake(FakeFrames([frame(0)] * 13), ww, NoiseTracker(), pressed=lambda: False, on_near=seen.append)
    assert seen == [0.3]
