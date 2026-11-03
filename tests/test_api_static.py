from fastapi.testclient import TestClient

import jarvis.api as api
from conftest import FakeLLM


def test_serves_built_page_and_keeps_api(cfg, tmp_path, monkeypatch):
    (tmp_path / "web" / "dist").mkdir(parents=True)
    (tmp_path / "web" / "dist" / "index.html").write_text("<h1>Jarvis page</h1>")
    monkeypatch.setattr(api, "ROOT", tmp_path)
    c = TestClient(api.create_app(cfg, FakeLLM([])))
    assert "Jarvis page" in c.get("/").text
    assert c.get("/health").json()["status"] == "ok"


def test_no_dist_means_api_only(cfg, tmp_path, monkeypatch):
    monkeypatch.setattr(api, "ROOT", tmp_path)
    c = TestClient(api.create_app(cfg, FakeLLM([])))
    assert c.get("/").status_code == 404
    assert c.get("/health").status_code == 200
