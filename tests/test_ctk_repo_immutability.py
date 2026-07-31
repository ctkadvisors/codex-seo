from pathlib import Path

from scripts.seo_pipeline_utils import cache_root, ensure_cache_gitignore, reports_root


def test_default_roots_use_xdg_and_never_edit_repo(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    gitignore = repo / ".gitignore"
    gitignore.write_bytes(b"owned-by-user\n")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    before = gitignore.read_bytes()
    ensure_cache_gitignore(repo)

    assert gitignore.read_bytes() == before
    assert cache_root() == (tmp_path / "cache" / "ctk-codex-seo").resolve()
    assert reports_root() == (tmp_path / "state" / "ctk-codex-seo" / "reports").resolve()
    assert not (repo / ".ctk-seo-cache").exists()
