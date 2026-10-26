"""Record the microphone to a WAV file (mono, 16-bit, 16 kHz: what Whisper wants).

The microphone is injected (`open_stream`), so tests never touch real audio.
"""
import shutil
import subprocess
import threading
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

SAMPLE_RATE = 16000
MAX_SECONDS = 30
QUIET_PEAK = 300  # int16 peak below this = almost nothing was recorded (max is 32767)


class RecorderError(Exception):
    """Plain-text problem the user can act on."""


@dataclass(frozen=True)
class Recording:
    path: Path
    seconds: float
    peak: int

    @property
    def silent(self) -> bool:
        return self.peak == 0

    @property
    def quiet(self) -> bool:
        return 0 < self.peak < QUIET_PEAK


def open_microphone(callback: Callable):
    """Real microphone stream (sounddevice, imported only here)."""
    try:
        import sounddevice as sd
    except (ImportError, OSError) as exc:  # OSError: PortAudio library missing
        raise RecorderError(f"audio library not available ({exc}). Run scripts/setup.sh again.") from exc
    try:
        return sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                              callback=lambda indata, frames, t, status: callback(indata))
    except sd.PortAudioError as exc:
        raise RecorderError(f"cannot open the microphone: {exc}") from exc


def list_input_devices() -> list[str]:
    try:
        import sounddevice as sd
    except (ImportError, OSError) as exc:
        raise RecorderError(f"audio library not available ({exc})") from exc
    default = sd.default.device[0]
    return [f"{'*' if i == default else ' '} {i}: {d['name']} ({int(d['default_samplerate'])} Hz)"
            for i, d in enumerate(sd.query_devices()) if d["max_input_channels"] > 0]


def write_wav(path: Path, audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio.astype("<i2").tobytes())


def record(path: Path, wait_for_enter: Callable[[], None], open_stream: Callable = open_microphone,
           max_seconds: float = MAX_SECONDS, say: Callable[[str], None] = print) -> Recording:
    """Enter starts, Enter stops (or max_seconds). Returns what was saved."""
    blocks: list[np.ndarray] = []
    say("Press Enter to start recording.")
    wait_for_enter()
    stream = open_stream(lambda indata: blocks.append(np.array(indata, dtype=np.int16).reshape(-1)))
    stream.start()
    say(f"Recording... press Enter to stop (max {max_seconds:g} s).")
    stop = threading.Event()

    def waiter() -> None:
        try:
            wait_for_enter()
        finally:
            stop.set()

    threading.Thread(target=waiter, daemon=True).start()
    stop.wait(max_seconds)
    stream.stop()
    stream.close()
    audio = np.concatenate(blocks) if blocks else np.zeros(0, dtype=np.int16)
    if audio.size == 0:
        raise RecorderError("nothing was recorded")
    write_wav(path, audio)
    return Recording(path=path, seconds=audio.size / SAMPLE_RATE, peak=int(np.abs(audio.astype(np.int32)).max()))


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as f:
        return np.frombuffer(f.readframes(f.getnframes()), dtype="<i2"), f.getframerate()


def advice(rec: Recording) -> str | None:
    if rec.silent:
        return ("The recording is completely silent. On macOS this usually means Terminal has no microphone "
                "permission: System Settings > Privacy & Security > Microphone > turn on Terminal, "
                "then restart Terminal.")
    if rec.quiet:
        return "The recording is very quiet. Check the input device (jarvis --devices) and the input volume."
    return None


def play(path: Path) -> bool:
    """Play with macOS afplay. False if afplay does not exist."""
    player = shutil.which("afplay")
    if not player:
        return False
    subprocess.run([player, str(path)], check=False)
    return True
