from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from scripts import google_auth, sync_flow
from scripts.security_redaction import redact


def test_default_google_oauth_is_read_only():
    assert google_auth.OAUTH_SCOPES.split() == [
        "https://www.googleapis.com/auth/webmasters.readonly",
        "https://www.googleapis.com/auth/analytics.readonly",
    ]


def test_token_write_is_atomic_and_private(tmp_path: Path, monkeypatch):
    token = tmp_path / "config" / "oauth-token.json"
    monkeypatch.setattr(google_auth, "TOKEN_PATH", str(token))

    google_auth._save_oauth_token({"access_token": "secret", "refresh_token": "refresh"})

    assert json.loads(token.read_text())["access_token"] == "secret"
    assert stat.S_IMODE(token.stat().st_mode) == 0o600
    assert stat.S_IMODE(token.parent.stat().st_mode) == 0o700
    assert not list(token.parent.glob(f".{token.name}.*"))


def test_redaction_covers_common_credentials():
    value = {
        "Authorization": "Bearer abc",
        "client_secret": "xyz",
        "nested": {"refresh_token": "refresh", "safe": "yes"},
    }
    assert redact(value) == {
        "Authorization": "[REDACTED]",
        "client_secret": "[REDACTED]",
        "nested": {"refresh_token": "[REDACTED]", "safe": "yes"},
    }


def test_sync_flow_never_invokes_gh_for_implicit_credentials(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "env-token")

    def forbidden(*args, **kwargs):
        raise AssertionError("subprocess credential discovery is forbidden")

    monkeypatch.setattr(sync_flow.subprocess, "run", forbidden)
    assert sync_flow._authed_headers()["Authorization"] == "Bearer env-token"

    monkeypatch.delenv("GITHUB_TOKEN")
    assert "Authorization" not in sync_flow._authed_headers()
