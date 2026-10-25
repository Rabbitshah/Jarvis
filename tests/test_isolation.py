"""The test suite must never read or change your real notes or your real index."""
from pathlib import Path

from conftest import REAL_DATA, fingerprint
from jarvis.config import load_config


def test_default_config_points_away_from_real_data():
    cfg = load_config()
    for real in REAL_DATA:
        assert not cfg.notes_dir.is_relative_to(real) and not cfg.index_dir.is_relative_to(real)
    assert cfg.notes_dir != REAL_DATA[0] and cfg.index_dir != REAL_DATA[1]


def test_cfg_fixture_uses_temp_folders(cfg, tmp_path):
    assert cfg.notes_dir.is_relative_to(tmp_path) and cfg.index_dir.is_relative_to(tmp_path)


def test_fingerprint_sees_changes(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("one")
    first = fingerprint(tmp_path)
    f.write_text("one two")
    assert fingerprint(tmp_path) != first                     # edit is noticed
    (tmp_path / "b.md").write_text("x")
    assert len(fingerprint(tmp_path)) == 2                    # new file is noticed
    assert fingerprint(tmp_path / "missing") == []


def test_search_with_default_config_cannot_reach_the_real_index():
    from jarvis.memory.search import search_notes
    from jarvis.memory.store import StoreError
    import pytest
    with pytest.raises(StoreError, match="does not exist"):       # temp index is empty, real one is not used
        search_notes(load_config(), lambda t: [[1.0, 0.0]], "anything")
