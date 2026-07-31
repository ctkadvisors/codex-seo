from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts.ctk_install import MARKETPLACE_NAME, install, marketplace_root, uninstall
from scripts.security_paths import resolve_beneath


def snapshot(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


@pytest.fixture
def source_tree(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / ".codex-plugin").mkdir(parents=True)
    (source / ".codex-plugin" / "plugin.json").write_text(
        json.dumps({"name": "ctk-codex-seo", "version": "2.0.0"}),
        encoding="utf-8",
    )
    (source / "skills" / "ctk-seo").mkdir(parents=True)
    (source / "skills" / "ctk-seo" / "SKILL.md").write_text("safe\n", encoding="utf-8")
    (source / ".git").mkdir()
    (source / ".git" / "secret").write_text("never copy", encoding="utf-8")
    return source


@pytest.fixture
def codex_calls():
    calls: list[tuple[list[str], dict[str, str]]] = []

    def run(args: list[str], env: dict[str, str]):
        calls.append((args, env))
        return subprocess.CompletedProcess(args, 0, stdout="{}", stderr="")

    return calls, run


def test_fresh_install_is_registered_marketplace_and_manifested(
    tmp_path: Path, source_tree: Path, codex_calls
):
    home = tmp_path / "codex"
    calls, runner = codex_calls
    result = install(source_tree, home, command_runner=runner)
    root = marketplace_root(home)
    target = root / "plugins" / "ctk-codex-seo"

    assert result.ok
    assert (target / "skills" / "ctk-seo" / "SKILL.md").read_text() == "safe\n"
    assert not (target / ".git").exists()
    marketplace = json.loads((root / ".agents" / "plugins" / "marketplace.json").read_text())
    assert marketplace["name"] == MARKETPLACE_NAME
    assert marketplace["plugins"][0]["source"]["path"] == "./plugins/ctk-codex-seo"
    manifest = json.loads((root / "install-manifest.json").read_text())
    entry = next(item for item in manifest["files"] if item["path"].endswith("SKILL.md"))
    assert entry["sha256"] == hashlib.sha256(b"safe\n").hexdigest()
    assert [call[0] for call in calls] == [
        ["codex", "plugin", "marketplace", "add", str(root), "--json"],
        ["codex", "plugin", "add", f"ctk-codex-seo@{MARKETPLACE_NAME}", "--json"],
    ]
    assert all(call[1]["CODEX_HOME"] == str(home.resolve()) for call in calls)


def test_collision_fails_without_persistent_write(tmp_path: Path, source_tree: Path, codex_calls):
    home = tmp_path / "codex"
    foreign = marketplace_root(home)
    foreign.mkdir(parents=True)
    (foreign / "foreign.txt").write_bytes(b"keep-me")
    before = snapshot(home)

    result = install(source_tree, home, command_runner=codex_calls[1])

    assert not result.ok and result.code == "collision"
    assert snapshot(home) == before


def test_update_requires_valid_ownership_and_preserves_unrelated_state(
    tmp_path: Path, source_tree: Path, codex_calls
):
    home = tmp_path / "codex"
    unrelated = home / "skills" / "someone-else" / "SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_bytes(b"untouched")
    assert install(source_tree, home, command_runner=codex_calls[1]).ok
    (source_tree / "skills" / "ctk-seo" / "SKILL.md").write_text("updated\n")

    assert install(source_tree, home, command_runner=codex_calls[1]).ok
    assert unrelated.read_bytes() == b"untouched"
    target = marketplace_root(home) / "plugins" / "ctk-codex-seo"
    assert (target / "skills" / "ctk-seo" / "SKILL.md").read_text() == "updated\n"


def test_corrupt_manifest_refuses_update(tmp_path: Path, source_tree: Path, codex_calls):
    home = tmp_path / "codex"
    assert install(source_tree, home, command_runner=codex_calls[1]).ok
    manifest = marketplace_root(home) / "install-manifest.json"
    manifest.write_text("{}")
    before = snapshot(home)

    result = install(source_tree, home, command_runner=codex_calls[1])

    assert not result.ok and result.code == "ownership_invalid"
    assert snapshot(home) == before


def test_uninstall_preserves_modified_owned_files(tmp_path: Path, source_tree: Path, codex_calls):
    home = tmp_path / "codex"
    calls, runner = codex_calls
    assert install(source_tree, home, command_runner=runner).ok
    calls.clear()
    target = marketplace_root(home) / "plugins" / "ctk-codex-seo"
    modified = target / "skills" / "ctk-seo" / "SKILL.md"
    modified.write_text("my edits\n")

    result = uninstall(home, command_runner=runner)

    assert not result.ok and result.code == "modified_files"
    assert modified.read_text() == "my edits\n"
    assert (target / ".codex-plugin" / "plugin.json").exists()
    assert calls == []


def test_registration_failure_rolls_back_filesystem(tmp_path: Path, source_tree: Path):
    home = tmp_path / "codex"
    unrelated = home / "keep"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_bytes(b"unchanged")
    before = snapshot(home)

    def fail(args: list[str], env: dict[str, str]):
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="registration failed")

    result = install(source_tree, home, command_runner=fail)

    assert not result.ok and result.code == "registration_failed"
    assert snapshot(home) == before


def test_symlink_source_and_traversal_are_rejected(tmp_path: Path, source_tree: Path):
    os.symlink(source_tree / "skills", source_tree / "linked")
    result = install(source_tree, tmp_path / "codex", command_runner=lambda *_: None)
    assert not result.ok and result.code == "unsafe_source"

    with pytest.raises(ValueError):
        resolve_beneath(tmp_path, "../escape")
