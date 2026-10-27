"""Text to speech with Piper, which runs as its own local server (scripts/piper-up.sh).

Piper is GPL-3.0 and Jarvis is MIT, so Jarvis only talks to it over HTTP and never imports it.
"""
import re
import shutil
import subprocess
from pathlib import Path

import httpx

MAX_SPOKEN_CHARS = 500  # a long answer is shown, not read out for a minute


class TtsError(Exception):
    """Plain-text problem the user can act on."""


def speakable(text: str, limit: int = MAX_SPOKEN_CHARS) -> str:
    """Make a reply fit for speaking: no markdown, no links, not too long."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"https?://\S+", "a link", text)
    text = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_`#>|~]+", "", text)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    return (cut[:end + 1] if end > limit // 3 else cut.rsplit(" ", 1)[0]).strip()


class PiperClient:
    def __init__(self, base_url: str, voice: str, timeout: float = 30.0, transport: httpx.BaseTransport | None = None,
                 length_scale: float = 1.0):
        self.voice = voice
        self.length_scale = length_scale  # below 1 = faster speech
        self._http = httpx.Client(base_url=base_url, timeout=timeout, transport=transport)

    def ping(self) -> bool:
        try:
            return self._http.get("/voices", timeout=2.0).status_code == 200
        except httpx.HTTPError:
            return False

    def synthesize(self, text: str) -> bytes:
        """Text -> WAV bytes."""
        try:
            r = self._http.post("/synthesize", json={"text": text, "voice": self.voice,
                                                   "length_scale": self.length_scale})
        except httpx.HTTPError as exc:
            raise TtsError(f"Piper is not reachable ({exc}). Start it with scripts/piper-up.sh") from exc
        if r.status_code != 200:
            raise TtsError(f"Piper returned {r.status_code}: {r.text[:200]}")
        return r.content


class Player:
    """Plays WAV bytes with macOS afplay, one at a time. stop() cuts the current sound."""

    def __init__(self, path: Path):
        self.path = path
        self._proc: subprocess.Popen | None = None

    def available(self) -> bool:
        return shutil.which("afplay") is not None

    def play(self, wav: bytes) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(wav)
        self._proc = subprocess.Popen([shutil.which("afplay") or "afplay", str(self.path)])
        self._proc.wait()

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()


def play_wav_bytes(wav: bytes, path: Path) -> bool:
    """Write the WAV to path and play it with macOS afplay (blocks until done). False without afplay."""
    player = shutil.which("afplay")
    if not player:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(wav)
    subprocess.run([player, str(path)], check=False)
    return True
