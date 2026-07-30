#!/usr/bin/env python3
"""Deterministically namespace upstream SEO plugin resources for CTK.

This migration is intentionally repository-scoped. It refuses to run with a
dirty worktree, never overwrites a destination, and supports a read-only
``--check`` mode for CI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".ps1", ".toml", ".txt", ".yml", ".yaml"}
SKILL_TOKEN = re.compile(r"(?<!ctk-)\bseo(?=-[a-z0-9]|[/'\"`])")


def git_status() -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def mappings() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for source in sorted((ROOT / "skills").glob("seo*")):
        pairs.append((source, source.with_name(f"ctk-{source.name}")))
    for source in sorted((ROOT / "agents").glob("seo-*.toml")):
        pairs.append((source, source.with_name(f"ctk-{source.name}")))
    return pairs


def rewritten_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = SKILL_TOKEN.sub("ctk-seo", text)
    if path == ROOT / ".codex-plugin" / "plugin.json":
        data = json.loads(text)
        data["name"] = "ctk-codex-seo"
        data["version"] = "2.0.0"
        data["description"] = (
            "Security-hardened, non-destructive SEO analysis suite maintained by CTK Advisors."
        )
        data["author"] = {
            "name": "CTK Advisors",
            "url": "https://github.com/ctkadvisors",
        }
        data["homepage"] = "https://github.com/ctkadvisors/codex-seo"
        data["repository"] = "https://github.com/ctkadvisors/codex-seo"
        data["interface"]["displayName"] = "CTK Codex SEO"
        data["interface"]["developerName"] = "CTK Advisors"
        text = json.dumps(data, indent=2) + "\n"
    return text


def text_files() -> list[Path]:
    ignored = {".git", ".venv", "__pycache__"}
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix in TEXT_SUFFIXES
        and not any(part in ignored for part in path.parts)
    ]


def pending_changes() -> list[str]:
    changes: list[str] = []
    for source, destination in mappings():
        if destination.exists():
            raise RuntimeError(f"namespace destination already exists: {destination}")
        changes.append(f"move {source.relative_to(ROOT)} -> {destination.relative_to(ROOT)}")
    for path in text_files():
        if rewritten_text(path) != path.read_text(encoding="utf-8"):
            changes.append(f"rewrite {path.relative_to(ROOT)}")
    return changes


def apply() -> list[str]:
    changes = pending_changes()
    for source, destination in mappings():
        source.rename(destination)
    for path in text_files():
        updated = rewritten_text(path)
        if updated != path.read_text(encoding="utf-8"):
            path.write_text(updated, encoding="utf-8")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit nonzero when migration is pending")
    args = parser.parse_args()

    status = git_status()
    if status:
        print("refusing namespace migration with a dirty worktree", file=sys.stderr)
        print(status, file=sys.stderr)
        return 2

    changes = pending_changes()
    if args.check:
        if changes:
            print("\n".join(changes))
            return 1
        print("CTK namespace migration is complete")
        return 0

    for change in apply():
        print(change)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
