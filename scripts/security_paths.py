"""Fail-closed filesystem primitives used by CTK installers and credential code."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


def resolve_beneath(root: Path, relative: str | Path) -> Path:
    root = root.expanduser().resolve()
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes root: {relative}")
    return candidate


def reject_symlink_components(path: Path, *, stop: Path | None = None) -> None:
    current = path
    boundary = stop.resolve() if stop else None
    while True:
        if current.is_symlink():
            raise ValueError(f"symlink path component is not allowed: {current}")
        if boundary is not None and current.resolve() == boundary:
            return
        if current == current.parent:
            return
        current = current.parent


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    reject_symlink_components(path.parent)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_owned_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or (not path.is_file() and not path.is_dir()):
            raise ValueError(f"unexpected file type: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hash_file(path)
    return result
