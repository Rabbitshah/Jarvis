import httpx
import pytest

from jarvis.voice import tts


def test_speakable_strips_markdown_links_and_lists():
    raw = "## Plan\n- **Apply** to `York`\n- see https://example.com/x\n```\ncode\n```\n1. Done"
    assert tts.speakable(raw) == "Plan Apply to York see a link Done"


def test_speakable_cuts_long_text_at_a_sentence():
    text = "First sentence here. " * 40
    out = tts.speakable(text, limit=100)
    assert len(out) <= 100 and out.endswith(".")


def test_speakable_empty():
    assert tts.speakable("```code```") == ""


def make(handler):
    return tts.PiperClient("http://piper", "v", transport=httpx.MockTransport(handler))


def test_synthesize_posts_text_and_voice():
    seen = {}

    def handler(req):
        seen["body"] = req.read()
        return httpx.Response(200, content=b"RIFFxxxx")

    assert make(handler).synthesize("hi") == b"RIFFxxxx"
    assert b'"text"' in seen["body"] and b'"voice"' in seen["body"]


def test_errors_are_plain():
    with pytest.raises(tts.TtsError, match="500"):
        make(lambda r: httpx.Response(500, text="boom")).synthesize("hi")

    def down(req):
        raise httpx.ConnectError("refused")

    with pytest.raises(tts.TtsError, match="piper-up.sh"):
        make(down).synthesize("hi")
    assert make(down).ping() is False
    assert make(lambda r: httpx.Response(200, json=[])).ping() is True


def test_play_without_afplay(monkeypatch, tmp_path):
    monkeypatch.setattr(tts.shutil, "which", lambda n: None)
    assert tts.play_wav_bytes(b"x", tmp_path / "r.wav") is False
    assert not (tmp_path / "r.wav").exists()


def test_speed_is_sent_to_piper():
    seen = {}

    def handler(req):
        seen["body"] = req.read()
        return httpx.Response(200, content=b"W")

    tts.PiperClient("http://piper", "v", transport=httpx.MockTransport(handler), length_scale=0.8).synthesize("hi")
    assert b'"length_scale":0.8' in seen["body"]
