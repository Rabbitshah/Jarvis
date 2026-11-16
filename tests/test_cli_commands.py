"""Every command that main() dispatches to must exist (a bad edit once deleted two of them and nothing noticed)."""
import ast
from pathlib import Path

import jarvis.cli as cli


def test_every_name_called_in_main_is_defined():
    tree = ast.parse(Path(cli.__file__).read_text(encoding="utf-8"))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    called = {c.func.id for c in ast.walk(main) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
    commands = {n for n in called if n.endswith("_cmd") or n.endswith("_loop")}
    missing = sorted(n for n in commands if not hasattr(cli, n))
    assert not missing, f"cli.main() calls functions that do not exist: {missing}"
    assert {"record_cmd", "transcribe_cmd", "devices_cmd", "listen_loop", "voice_loop"} <= commands
