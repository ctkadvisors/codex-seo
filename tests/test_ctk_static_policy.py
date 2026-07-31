from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_production_scripts_do_not_bypass_network_adapter():
    violations = []
    allowed = {"security_network.py"}
    production_paths = list((ROOT / "scripts").glob("*.py"))
    production_paths += list((ROOT / "extensions").glob("*/scripts/*.py"))
    for path in production_paths:
        if path.name in allowed:
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name == "requests" for alias in node.names):
                    violations.append(f"{path.name}:{node.lineno}: requests")
            if isinstance(node, ast.ImportFrom):
                if (node.module or "") == "requests":
                    violations.append(f"{path.name}:{node.lineno}: requests")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"urlopen", "create_connection"}:
                    violations.append(f"{path.name}:{node.lineno}: {node.func.id}")
    assert violations == []


def test_no_shell_or_ambient_credential_discovery():
    paths = list((ROOT / "scripts").glob("*.py"))
    paths += list((ROOT / "extensions").glob("*/scripts/*.py"))
    text = "\n".join(path.read_text() for path in paths)
    assert "shell=True" not in text
    assert '"gh", "auth", "token"' not in text


def test_extension_wrappers_cannot_mutate_global_codex_state():
    wrappers = []
    for pattern in ("*/install.sh", "*/uninstall.sh", "*/install.ps1", "*/uninstall.ps1"):
        wrappers.extend((ROOT / "extensions").glob(pattern))
    forbidden = (
        "rm -rf",
        "Remove-Item",
        "settings.json",
        "Copy-Item",
        "\ncp ",
        "npx ",
        "pip install",
    )
    for path in wrappers:
        text = path.read_text()
        assert all(token not in text for token in forbidden), path
