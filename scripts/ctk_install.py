#!/usr/bin/env python3
"""Transactional, ownership-aware installer for the CTK Codex SEO plugin."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    from .security_paths import atomic_write, hash_file, reject_symlink_components
except ImportError:  # Direct script execution.
    from security_paths import atomic_write, hash_file, reject_symlink_components


PLUGIN_NAME = "ctk-codex-seo"
MANIFEST_NAME = "install-manifest.json"
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"}


@dataclass(frozen=True)
class Result:
    ok: bool
    code: str
    details: tuple[str, ...] = field(default_factory=tuple)


def _target(codex_home: Path) -> Path:
    return codex_home.expanduser().resolve() / "plugins" / PLUGIN_NAME


def _source_files(source: Path) -> list[Path]:
    source = source.expanduser().resolve()
    files: list[Path] = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"source contains symlink: {relative}")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ValueError(f"source contains unexpected file type: {relative}")
    return files


def _read_manifest(target: Path) -> dict:
    path = target / MANIFEST_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("missing or invalid ownership manifest") from exc
    if data.get("plugin") != PLUGIN_NAME or data.get("schema") != 1:
        raise ValueError("ownership manifest does not identify this plugin")
    files = data.get("files")
    if not isinstance(files, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and isinstance(item.get("sha256"), str)
        and not Path(item["path"]).is_absolute()
        and ".." not in Path(item["path"]).parts
        for item in files
    ):
        raise ValueError("ownership manifest file list is invalid")
    return data


def _modified_owned_files(target: Path, manifest: dict) -> list[str]:
    modified: list[str] = []
    for item in manifest["files"]:
        path = target / item["path"]
        if path.is_symlink() or not path.is_file() or hash_file(path) != item["sha256"]:
            modified.append(item["path"])
    return modified


def _build_stage(source: Path, stage: Path) -> None:
    entries = []
    for source_file in _source_files(source):
        relative = source_file.relative_to(source)
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_file, destination, follow_symlinks=False)
        os.chmod(destination, source_file.stat().st_mode & 0o777)
        entries.append({"path": relative.as_posix(), "sha256": hash_file(destination)})
    manifest = {
        "schema": 1,
        "plugin": PLUGIN_NAME,
        "files": entries,
    }
    atomic_write(
        stage / MANIFEST_NAME,
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
        0o600,
    )
    _read_manifest(stage)


def install(source: Path, codex_home: Path) -> Result:
    source = source.expanduser().resolve()
    target = _target(codex_home)
    try:
        reject_symlink_components(source)
        _source_files(source)
    except ValueError as exc:
        return Result(False, "unsafe_source", (str(exc),))
    if not (source / ".codex-plugin" / "plugin.json").is_file():
        return Result(False, "invalid_source", ("missing plugin manifest",))

    existing_manifest = None
    if target.exists():
        if target.is_symlink() or not target.is_dir():
            return Result(False, "collision")
        if not (target / MANIFEST_NAME).is_file():
            return Result(False, "collision")
        try:
            existing_manifest = _read_manifest(target)
        except ValueError as exc:
            return Result(False, "ownership_invalid", (str(exc),))
        modified = _modified_owned_files(target, existing_manifest)
        if modified:
            return Result(False, "owned_files_modified", tuple(modified))

    plugins = target.parent
    plugins.mkdir(parents=True, exist_ok=True)
    if plugins.is_symlink():
        return Result(False, "unsafe_destination")
    stage = Path(tempfile.mkdtemp(prefix=f".{PLUGIN_NAME}.stage-", dir=plugins))
    rollback = plugins / f".{PLUGIN_NAME}.rollback-{os.getpid()}"
    try:
        _build_stage(source, stage)
        if target.exists():
            if rollback.exists():
                return Result(False, "unsafe_destination")
            os.replace(target, rollback)
        try:
            os.replace(stage, target)
        except Exception:
            if rollback.exists() and not target.exists():
                os.replace(rollback, target)
            raise
        _read_manifest(target)
        if rollback.exists():
            shutil.rmtree(rollback)
        return Result(True, "installed")
    except (OSError, ValueError) as exc:
        return Result(False, "install_failed", (str(exc),))
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def uninstall(codex_home: Path, *, force_owned_modifications: bool = False) -> Result:
    target = _target(codex_home)
    if not target.exists():
        return Result(True, "not_installed")
    try:
        manifest = _read_manifest(target)
    except ValueError as exc:
        return Result(False, "ownership_invalid", (str(exc),))
    modified = _modified_owned_files(target, manifest)
    if force_owned_modifications:
        shutil.rmtree(target)
        return Result(True, "uninstalled")

    modified_set = set(modified)
    for item in manifest["files"]:
        if item["path"] not in modified_set:
            (target / item["path"]).unlink()
    for directory in sorted((p for p in target.rglob("*") if p.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    if modified:
        return Result(False, "modified_files", tuple(modified))
    (target / MANIFEST_NAME).unlink(missing_ok=True)
    target.rmdir()
    return Result(True, "uninstalled")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    install_parser = subcommands.add_parser("install")
    install_parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    install_parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", "~/.codex")))
    uninstall_parser = subcommands.add_parser("uninstall")
    uninstall_parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", "~/.codex")))
    uninstall_parser.add_argument("--force-owned-modifications", action="store_true")
    args = parser.parse_args()
    result = (
        install(args.source, args.codex_home)
        if args.command == "install"
        else uninstall(args.codex_home, force_owned_modifications=args.force_owned_modifications)
    )
    print(json.dumps({"ok": result.ok, "code": result.code, "details": result.details}))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
