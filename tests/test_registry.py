from jarvis.tools.builtin import build_registry


def test_tool_names(cfg):
    assert build_registry(cfg).names() == ["get_time", "list_notes", "read_note"]


def test_unknown_tool(cfg):
    assert "unknown tool" in build_registry(cfg).call("nope", {})


def test_bad_args_do_not_crash(cfg):
    out = build_registry(cfg).call("read_note", {"wrong": 1})
    assert out == "error: missing required argument 'path'"


def test_string_args_parsed(cfg):
    assert "December" in build_registry(cfg).call("read_note", '{"path": "idea.md"}')


def test_invalid_json_args(cfg):
    assert "not valid JSON" in build_registry(cfg).call("read_note", "{oops")


def test_get_time_plain_words(cfg):
    out = build_registry(cfg).call("get_time", {})
    assert out.startswith("It is ") and ("AM" in out or "PM" in out) and "local time" in out


def test_schema_shape(cfg):
    s = build_registry(cfg).schemas()[0]
    assert s["type"] == "function" and "name" in s["function"]
