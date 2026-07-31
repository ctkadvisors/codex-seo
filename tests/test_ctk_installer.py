from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from scripts.ctk_install import install, uninstall
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


def test_fresh_install_is_self_contained_and_manifested(tmp_path: Path, source_tree: Path):
    home = tmp_path / "codex"
    result = install(source_tree, home)
    target = home / "plugins" / "ctk-codex-seo"

    assert result.ok
    assert (target / "skills" / "ctk-seo" / "SKILL.md").read_text() == "safe\n"
    assert not (target / ".git").exists()
    manifest = json.loads((target / "install-manifest.json").read_text())
    entry = next(item for item in manifest["files"] if item["path"].endswith("SKILL.md"))
    assert entry["sha256"] == hashlib.sha256(b"safe\n").hexdigest()


def test_collision_fails_without_persistent_write(tmp_path: Path, source_tree: Path):
    home = tmp_path / "codex"
    foreign = home / "plugins" / "ctk-codex-seo"
    foreign.mkdir(parents=True)
    (foreign / "foreign.txt").write_bytes(b"keep-me")
    before = snapshot(home)

    result = install(source_tree, home)

    assert not result.ok and result.code == "collision"
    assert snapshot(home) == before


def test_update_requires_valid_ownership_and_preserves_unrelated_state(tmp_path: Path, source_tree: Path):
    home = tmp_path / "codex"
    unrelated = home / "skills" / "someone-else" / "SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_bytes(b"untouched")
    assert install(source_tree, home).ok
    (source_tree / "skills" / "ctk-seo" / "SKILL.md").write_text("updated\n")

    assert install(source_tree, home).ok
    assert unrelated.read_bytes() == b"untouched"
    assert (home / "plugins" / "ctk-codex-seo" / "skills" / "ctk-seo" / "SKILL.md").read_text() == "updated\n"


def test_corrupt_manifest_refuses_update(tmp_path: Path, source_tree: Path):
    home = tmp_path / "codex"
    assert install(source_tree, home).ok
    manifest = home / "plugins" / "ctk-codex-seo" / "install-manifest.json"
    manifest.write_text("{}")
    before = snapshot(home)

    result = install(source_tree, home)

    assert not result.ok and result.code == "ownership_invalid"
    assert snapshot(home) == before


def test_uninstall_preserves_modified_owned_files(tmp_path: Path, source_tree: Path):
    home = tmp_path / "codex"
    assert install(source_tree, home).ok
    target = home / "plugins" / "ctk-codex-seo"
    modified = target / "skills" / "ctk-seo" / "SKILL.md"
    modified.write_text("my edits\n")

    result = uninstall(home)

    assert not result.ok and result.code == "modified_files"
    assert modified.read_text() == "my edits\n"
    assert not (target / ".codex-plugin" / "plugin.json").exists()


def test_symlink_source_and_traversal_are_rejected(tmp_path: Path, source_tree: Path):
    os.symlink(source_tree / "skills", source_tree / "linked")
    result = install(source_tree, tmp_path / "codex")
    assert not result.ok and result.code == "unsafe_source"

    with pytest.raises(ValueError):
        resolve_beneath(tmp_path, "../escape")
