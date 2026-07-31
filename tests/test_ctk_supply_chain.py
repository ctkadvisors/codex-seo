from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_core_lock_is_exact_and_hashed():
    lock = (ROOT / "requirements" / "core.txt").read_text(encoding="utf-8")
    package_lines = [
        line for line in lock.splitlines()
        if line and not line.startswith((" ", "#", "--"))
    ]
    assert package_lines
    assert all(re.match(r"^[A-Za-z0-9_.-]+==[^ ]+ \\$", line) for line in package_lines)
    assert lock.count("--hash=sha256:") >= len(package_lines)


def test_bootstrap_enforces_reviewed_core_only():
    source = (ROOT / "scripts" / "bootstrap_environment.py").read_text(encoding="utf-8")
    assert '"--require-hashes"' in source
    assert '"--only-binary=:all:"' in source
    assert "requirements\" / \"core.txt" in source
    assert "playwright install" not in source
    assert "requirements-optional" not in source
    assert "pip\", \"install\", \"--upgrade\"" not in source
