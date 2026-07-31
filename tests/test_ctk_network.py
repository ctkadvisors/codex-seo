from __future__ import annotations

import socket

import pytest

from scripts.security_network import MAX_RESPONSE_BYTES, SafeRequests, validate_public_url


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


def test_requests_facade_supports_every_production_attribute():
    client = SafeRequests()
    assert callable(client.get)
    assert callable(client.post)
    assert callable(client.head)
    assert issubclass(client.HTTPError, Exception)


def test_credentials_are_rejected_before_unapproved_egress(monkeypatch):
    client = SafeRequests()
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))],
    )

    with pytest.raises(ValueError, match="credentials"):
        client.get("https://example.com", params={"key": "secret"})


def test_chunked_response_limit_is_enforced():
    class Response:
        headers = {}
        status_code = 200

        def iter_content(self, chunk_size=1, decode_unicode=False):
            yield b"x" * MAX_RESPONSE_BYTES
            yield b"x"

    client = SafeRequests()
    response = Response()
    client._enforce_stream_limit(response)
    with pytest.raises(ValueError, match="size limit"):
        list(response.iter_content())
