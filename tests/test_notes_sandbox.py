import pytest

from jarvis.tools import notes
from jarvis.tools.registry import ToolError


def test_reads_note(cfg):
    assert "December" in notes.read_note(cfg.notes_dir, "idea.md")


def test_blocks_parent_traversal(cfg):
    (cfg.notes_dir.parent / "secret.md").write_text("secret")
    with pytest.raises(ToolError, match="escapes"):
        notes.read_note(cfg.notes_dir, "../secret.md")


def test_blocks_absolute_path(cfg):
    with pytest.raises(ToolError, match="absolute"):
        notes.read_note(cfg.notes_dir, "/etc/passwd")


def test_blocks_symlink_escape(cfg):
    outside = cfg.notes_dir.parent / "outside.md"
    outside.write_text("secret")
    (cfg.notes_dir / "link.md").symlink_to(outside)
    with pytest.raises(ToolError, match="escapes"):
        notes.read_note(cfg.notes_dir, "link.md")
    assert "link.md" not in notes.list_notes(cfg.notes_dir)


def test_blocks_wrong_extension(cfg):
    (cfg.notes_dir / "x.py").write_text("print(1)")
    with pytest.raises(ToolError, match="not a valid note name"):
        notes.read_note(cfg.notes_dir, "x.py")


def test_truncates_long_note(cfg):
    (cfg.notes_dir / "big.md").write_text("a" * (notes.MAX_CHARS + 50))
    assert "[truncated" in notes.read_note(cfg.notes_dir, "big.md")


def test_list_empty(cfg, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert notes.list_notes(empty) == "no notes found"


def test_missing_note_hints_list_notes(cfg):
    with pytest.raises(ToolError, match="list_notes"):
        notes.read_note(cfg.notes_dir, "nope.md")


def test_plain_name_matches_one_note(cfg):
    assert "December" in notes.read_note(cfg.notes_dir, "idea")
    assert "December" in notes.read_note(cfg.notes_dir, "IDEA.txt")


def test_ambiguous_name_lists_matches(cfg):
    (cfg.notes_dir / "idea-two.md").write_text("x")
    with pytest.raises(ToolError, match="several notes match"):
        notes.read_note(cfg.notes_dir, "idea")


def test_forgiving_match_never_escapes(cfg):
    (cfg.notes_dir.parent / "idea-secret.md").write_text("secret")
    with pytest.raises(ToolError, match="escapes"):
        notes.read_note(cfg.notes_dir, "../idea-secret.md")
