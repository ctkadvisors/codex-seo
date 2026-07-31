from __future__ import annotations

import socket

import pytest

from scripts.security_network import validate_public_url


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://user:pass@example.com",
        "http://127.0.0.1",
        "http://169.254.169.254/latest/meta-data",
        "http://[::1]",
        "http://[::ffff:127.0.0.1]",
    ],
)
def test_rejects_unsafe_urls(url: str):
    with pytest.raises(ValueError):
        validate_public_url(url)


def test_rejects_dns_resolving_to_private_address(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.2", 0))],
    )
    with pytest.raises(ValueError):
        validate_public_url("https://attacker.example")


def test_accepts_public_https(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))],
    )
    assert validate_public_url("https://example.com/a") == "https://example.com/a"
