#!/usr/bin/env python3
"""Transactional installer that registers CTK SEO through a local Codex marketplace."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

try:
    from .security_paths import atomic_write, hash_file, reject_symlink_components
except ImportError:  # Direct script execution.
    from security_paths import atomic_write, hash_file, reject_symlink_components


PLUGIN_NAME = "ctk-codex-seo"
MARKETPLACE_NAME = "ctk-advisors"
MANIFEST_NAME = "install-manifest.json"
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ctk-seo-cache",
}
CommandRunner = Callable[[list[str], dict[str, str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class Result:
    ok: bool
    code: str
    details: tuple[str, ...] = field(default_factory=tuple)


def marketplace_root(codex_home: Path) -> Path:
    return codex_home.expanduser().resolve() / "marketplaces" / MARKETPLACE_NAME


def _plugin_root(root: Path) -> Path:
    return root / "plugins" / PLUGIN_NAME


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


def _read_manifest(root: Path) -> dict:
    path = root / MANIFEST_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("missing or invalid ownership manifest") from exc
    if (
        data.get("plugin") != PLUGIN_NAME
        or data.get("marketplace") != MARKETPLACE_NAME
        or data.get("schema") != 2
    ):
        raise ValueError("ownership manifest does not identify this CTK marketplace")
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


def _modified_owned_files(root: Path, manifest: dict) -> list[str]:
    modified: list[str] = []
    for item in manifest["files"]:
        path = root / item["path"]
        if path.is_symlink() or not path.is_file() or hash_file(path) != item["sha256"]:
            modified.append(item["path"])
    return modified


def _marketplace_payload() -> dict:
    return {
        "name": MARKETPLACE_NAME,
        "interface": {"displayName": "CTK Advisors"},
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_USE",
                },
                "category": "Productivity",
            }
        ],
    }


def _build_stage(source: Path, stage: Path) -> None:
    entries: list[dict[str, str]] = []
    plugin_stage = _plugin_root(stage)
    for source_file in _source_files(source):
        relative = Path("plugins") / PLUGIN_NAME / source_file.relative_to(source)
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_file, destination, follow_symlinks=False)
        os.chmod(destination, source_file.stat().st_mode & 0o777)
        entries.append({"path": relative.as_posix(), "sha256": hash_file(destination)})

    plugin_manifest = json.loads(
        (plugin_stage / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    if plugin_manifest.get("name") != PLUGIN_NAME:
        raise ValueError("plugin manifest name does not match the CTK plugin")

    marketplace_path = stage / ".agents" / "plugins" / "marketplace.json"
    atomic_write(
        marketplace_path,
        (json.dumps(_marketplace_payload(), indent=2) + "\n").encode(),
        0o644,
    )
    entries.append(
        {
            "path": marketplace_path.relative_to(stage).as_posix(),
            "sha256": hash_file(marketplace_path),
        }
    )
    manifest = {
        "schema": 2,
        "plugin": PLUGIN_NAME,
        "marketplace": MARKETPLACE_NAME,
        "files": entries,
    }
    atomic_write(
        stage / MANIFEST_NAME,
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
        0o600,
    )
    _read_manifest(stage)


def _default_runner(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, env=env, capture_output=True, text=True, check=False)


def _run_codex(
    args: list[str],
    codex_home: Path,
    command_runner: CommandRunner,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["CODEX_HOME"] = str(codex_home.expanduser().resolve())
    return command_runner(["codex", *args], env)


def _register(
    root: Path,
    codex_home: Path,
    command_runner: CommandRunner,
    *,
    add_marketplace: bool,
) -> Result:
    if add_marketplace:
        result = _run_codex(
            ["plugin", "marketplace", "add", str(root), "--json"],
            codex_home,
            command_runner,
        )
        if result.returncode != 0:
            return Result(False, "registration_failed", (result.stderr.strip(),))
    result = _run_codex(
        ["plugin", "add", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}", "--json"],
        codex_home,
        command_runner,
    )
    if result.returncode != 0:
        if add_marketplace:
            _run_codex(
                ["plugin", "marketplace", "remove", MARKETPLACE_NAME, "--json"],
                codex_home,
                command_runner,
            )
        return Result(False, "registration_failed", (result.stderr.strip(),))
    return Result(True, "registered")


def _unregister(codex_home: Path, command_runner: CommandRunner) -> Result:
    remove_plugin = _run_codex(
        ["plugin", "remove", f"{PLUGIN_NAME}@{MARKETPLACE_NAME}", "--json"],
        codex_home,
        command_runner,
    )
    if remove_plugin.returncode != 0:
        return Result(False, "deregistration_failed", (remove_plugin.stderr.strip(),))
    remove_marketplace = _run_codex(
        ["plugin", "marketplace", "remove", MARKETPLACE_NAME, "--json"],
        codex_home,
        command_runner,
    )
    if remove_marketplace.returncode != 0:
        return Result(False, "deregistration_failed", (remove_marketplace.stderr.strip(),))
    return Result(True, "unregistered")


def install(
    source: Path,
    codex_home: Path,
    *,
    command_runner: CommandRunner = _default_runner,
) -> Result:
    source = source.expanduser().resolve()
    codex_home = codex_home.expanduser().resolve()
    root = marketplace_root(codex_home)
    try:
        reject_symlink_components(source)
        _source_files(source)
    except ValueError as exc:
        return Result(False, "unsafe_source", (str(exc),))
    if not (source / ".codex-plugin" / "plugin.json").is_file():
        return Result(False, "invalid_source", ("missing plugin manifest",))

    updating = root.exists()
    if updating:
        if root.is_symlink() or not root.is_dir():
            return Result(False, "collision")
        if not (root / MANIFEST_NAME).is_file():
            return Result(False, "collision")
        try:
            existing_manifest = _read_manifest(root)
        except ValueError as exc:
            return Result(False, "ownership_invalid", (str(exc),))
        modified = _modified_owned_files(root, existing_manifest)
        if modified:
            return Result(False, "owned_files_modified", tuple(modified))

    parent = root.parent
    parent.mkdir(parents=True, exist_ok=True)
    if parent.is_symlink():
        return Result(False, "unsafe_destination")
    stage = Path(tempfile.mkdtemp(prefix=f".{MARKETPLACE_NAME}.stage-", dir=parent))
    rollback = parent / f".{MARKETPLACE_NAME}.rollback-{os.getpid()}"
    try:
        _build_stage(source, stage)
        if updating:
            if rollback.exists():
                return Result(False, "unsafe_destination")
            os.replace(root, rollback)
        os.replace(stage, root)
        registration = _register(
            root,
            codex_home,
            command_runner,
            add_marketplace=not updating,
        )
        if not registration.ok:
            if root.exists():
                shutil.rmtree(root)
            if rollback.exists():
                os.replace(rollback, root)
                _register(root, codex_home, command_runner, add_marketplace=False)
            return registration
        if rollback.exists():
            shutil.rmtree(rollback)
        return Result(True, "installed")
    except FileNotFoundError as exc:
        if rollback.exists() and not root.exists():
            os.replace(rollback, root)
        return Result(False, "codex_cli_missing", (str(exc),))
    except (OSError, ValueError) as exc:
        if rollback.exists() and not root.exists():
            os.replace(rollback, root)
        return Result(False, "install_failed", (str(exc),))
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def uninstall(
    codex_home: Path,
    *,
    force_owned_modifications: bool = False,
    command_runner: CommandRunner = _default_runner,
) -> Result:
    codex_home = codex_home.expanduser().resolve()
    root = marketplace_root(codex_home)
    if not root.exists():
        return Result(True, "not_installed")
    try:
        manifest = _read_manifest(root)
    except ValueError as exc:
        return Result(False, "ownership_invalid", (str(exc),))
    modified = _modified_owned_files(root, manifest)
    if modified and not force_owned_modifications:
        return Result(False, "modified_files", tuple(modified))
    try:
        deregistration = _unregister(codex_home, command_runner)
    except FileNotFoundError as exc:
        return Result(False, "codex_cli_missing", (str(exc),))
    if not deregistration.ok:
        return deregistration
    shutil.rmtree(root)
    return Result(True, "uninstalled")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    install_parser = subcommands.add_parser("install")
    install_parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    install_parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", "~/.codex")),
    )
    uninstall_parser = subcommands.add_parser("uninstall")
    uninstall_parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", "~/.codex")),
    )
    uninstall_parser.add_argument("--force-owned-modifications", action="store_true")
    args = parser.parse_args()
    result = (
        install(args.source, args.codex_home)
        if args.command == "install"
        else uninstall(
            args.codex_home,
            force_owned_modifications=args.force_owned_modifications,
        )
    )
    print(json.dumps({"ok": result.ok, "code": result.code, "details": result.details}))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
