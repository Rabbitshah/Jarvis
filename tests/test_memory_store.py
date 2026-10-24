"""Vector store + embed client. No Ollama needed: embeddings are faked."""
import httpx
import pytest

from jarvis.llm import LLMError, OllamaClient
from jarvis.memory.store import StoreError, VectorStore, point_id


def test_one_vector_goes_in_and_comes_back(tmp_path):
    with VectorStore(tmp_path / "db", 3) as store:
        store.upsert([("a.md", 0, "alpha", [1, 0, 0]), ("b.md", 0, "beta", [0, 1, 0])])
        assert store.count() == 2
        hit = store.search([0.9, 0.1, 0], k=1)[0]
    assert (hit.file, hit.chunk, hit.text) == ("a.md", 0, "alpha")
    assert hit.score > 0.9


def test_data_survives_reopen(tmp_path):
    with VectorStore(tmp_path / "db", 3) as store:
        store.upsert([("a.md", 0, "alpha", [1, 0, 0])])
    with VectorStore(tmp_path / "db", 3) as store:
        assert store.count() == 1


def test_same_chunk_overwrites_not_duplicates(tmp_path):
    with VectorStore(tmp_path / "db", 3) as store:
        store.upsert([("a.md", 0, "old", [1, 0, 0])])
        store.upsert([("a.md", 0, "new", [1, 0, 0])])
        assert store.count() == 1
        assert store.search([1, 0, 0])[0].text == "new"
    assert point_id("a.md", 0) == point_id("a.md", 0) != point_id("a.md", 1)


def test_delete_file(tmp_path):
    with VectorStore(tmp_path / "db", 3) as store:
        store.upsert([("a.md", 0, "x", [1, 0, 0]), ("b.md", 0, "y", [0, 1, 0])])
        store.delete_file("a.md")
        assert store.count() == 1


def test_wrong_vector_size_is_a_clear_error(tmp_path):
    with VectorStore(tmp_path / "db", 3) as store:
        with pytest.raises(StoreError, match="expected 3"):
            store.upsert([("a.md", 0, "x", [1, 0])])
        with pytest.raises(StoreError, match="expected 3"):
            store.search([1, 0])


def test_model_change_is_detected(tmp_path):
    with VectorStore(tmp_path / "db", 3):
        pass
    with pytest.raises(StoreError, match="embedding model changed"):
        VectorStore(tmp_path / "db", 5).__enter__()


def test_locked_folder_gives_clear_error(tmp_path):
    with VectorStore(tmp_path / "db", 3):
        with pytest.raises(StoreError, match="in use"):
            VectorStore(tmp_path / "db", 3).__enter__()
    with VectorStore(tmp_path / "db", 3):  # lock released after close
        pass


def _client(handler):
    c = OllamaClient("http://x", "m", 5, "emb")
    c._http = httpx.Client(base_url="http://x", transport=httpx.MockTransport(handler))
    return c


def test_embed_sends_batch_and_returns_vectors():
    seen = {}

    def handler(req):
        seen["body"] = req.read()
        return httpx.Response(200, json={"embeddings": [[1.0, 2.0], [3.0, 4.0]]})

    out = _client(handler).embed(["a", "b"])
    assert out == [[1.0, 2.0], [3.0, 4.0]]
    assert req_json(seen["body"]) == {"model": "emb", "input": ["a", "b"]}


def req_json(raw):
    import json
    return json.loads(raw)


def test_embed_errors_are_clear():
    assert _client(lambda r: httpx.Response(200, json={})).embed([]) == []
    with pytest.raises(LLMError, match="ollama pull emb"):
        _client(lambda r: httpx.Response(404, json={"error": "nope"})).embed(["a"])
    with pytest.raises(LLMError, match="unexpected"):
        _client(lambda r: httpx.Response(200, json={"embeddings": [[1.0]]})).embed(["a", "b"])
    with pytest.raises(LLMError, match="500"):
        _client(lambda r: httpx.Response(500, text="boom")).embed(["a"])
