from jarvis.config import load_config


def test_defaults_load():
    cfg = load_config()
    assert cfg.model and cfg.ollama_url.startswith("http")
    assert cfg.notes_dir.is_absolute()


def test_env_override(monkeypatch):
    monkeypatch.setenv("JARVIS_MODEL", "other:1b")
    assert load_config().model == "other:1b"


def test_tts_settings(monkeypatch):
    cfg = load_config()
    assert cfg.tts_url.startswith("http://127.0.0.1") and cfg.tts_voice
    monkeypatch.setenv("JARVIS_TTS_URL", "http://127.0.0.1:1")
    assert load_config().tts_url == "http://127.0.0.1:1"
