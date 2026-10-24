from jarvis.config import load_config


def test_defaults_load():
    cfg = load_config()
    assert cfg.model and cfg.ollama_url.startswith("http")
    assert cfg.notes_dir.is_absolute()


def test_env_override(monkeypatch):
    monkeypatch.setenv("JARVIS_MODEL", "other:1b")
    assert load_config().model == "other:1b"
