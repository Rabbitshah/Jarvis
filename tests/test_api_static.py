
import jarvis.api as api
from conftest import FakeLLM, api_client


def test_serves_built_page_and_keeps_api(cfg, tmp_path, monkeypatch):
    (tmp_path / "web" / "dist").mkdir(parents=True)
    (tmp_path / "web" / "dist" / "index.html").write_text("<h1>Jarvis page</h1>")
    monkeypatch.setattr(api, "ROOT", tmp_path)
    c = api_client(api.create_app(cfg, FakeLLM([])), cfg)
    assert "Jarvis page" in c.get("/").text
    assert c.get("/health").json()["status"] == "ok"


def test_no_dist_means_api_only(cfg, tmp_path, monkeypatch):
    monkeypatch.setattr(api, "ROOT", tmp_path)
    c = api_client(api.create_app(cfg, FakeLLM([])), cfg)
    assert c.get("/").status_code == 404
    assert c.get("/health").status_code == 200
