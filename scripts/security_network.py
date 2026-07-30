"""Central outbound HTTP policy for CTK SEO workflows."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests as _requests


DEFAULT_TIMEOUT = (5, 30)
MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 25 * 1024 * 1024
USER_AGENT = "ctk-codex-seo/2.0 (+https://github.com/ctkadvisors/codex-seo)"
SENSITIVE_HOST_SUFFIXES = (
    "googleapis.com",
    "google.com",
    "github.com",
    "bing.com",
    "dataforseo.com",
    "moz.com",
    "openai.com",
)
SECRET_NAMES = {
    "authorization",
    "x-api-key",
    "api_key",
    "key",
    "access_token",
    "developer_token",
}


def _blocked(address: str) -> bool:
    ip = ipaddress.ip_address(address)
    if getattr(ip, "ipv4_mapped", None) is not None:
        ip = ip.ipv4_mapped
    return any(
        (
            ip.is_private,
            ip.is_loopback,
            ip.is_link_local,
            ip.is_reserved,
            ip.is_multicast,
            ip.is_unspecified,
        )
    )


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("only absolute HTTP(S) URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URL userinfo is forbidden")
    host = parsed.hostname.rstrip(".").lower()
    try:
        if _blocked(host):
            raise ValueError(f"blocked network address: {host}")
    except ValueError as exc:
        if str(exc).startswith("blocked"):
            raise
    try:
        addresses = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"unable to resolve host: {host}") from exc
    if not addresses or any(_blocked(item[4][0]) for item in addresses):
        raise ValueError(f"host resolves to a blocked network address: {host}")
    return url


def _contains_credentials(kwargs: dict) -> bool:
    for container_name in ("headers", "params", "data", "json"):
        container = kwargs.get(container_name)
        if isinstance(container, dict) and any(str(key).lower() in SECRET_NAMES for key in container):
            return True
    return False


def _sensitive_origin_allowed(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in SENSITIVE_HOST_SUFFIXES)


class SafeRequests:
    """Small requests-compatible facade enforcing URL and redirect policy."""

    RequestException = _requests.RequestException
    exceptions = _requests.exceptions
    Session = _requests.Session
    Response = _requests.Response
    PreparedRequest = _requests.PreparedRequest

    def __init__(self) -> None:
        self._session = _requests.Session()

    def request(self, method: str, url: str, **kwargs):
        sensitive = _contains_credentials(kwargs)
        if sensitive and not _sensitive_origin_allowed(url):
            raise ValueError("credentials may only be sent to an approved provider origin")
        timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
        kwargs.pop("allow_redirects", None)
        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("User-Agent", USER_AGENT)
        current = validate_public_url(url)
        initial_origin = urlparse(current).netloc.lower()
        for redirect_count in range(MAX_REDIRECTS + 1):
            response = self._session.request(
                method,
                current,
                headers=headers,
                timeout=timeout,
                allow_redirects=False,
                **kwargs,
            )
            length = response.headers.get("Content-Length")
            if length and int(length) > MAX_RESPONSE_BYTES:
                response.close()
                raise ValueError("response exceeds size limit")
            if response.status_code not in {301, 302, 303, 307, 308}:
                return response
            if redirect_count == MAX_REDIRECTS:
                response.close()
                raise ValueError("redirect limit exceeded")
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise ValueError("redirect is missing Location")
            current = validate_public_url(urljoin(current, location))
            if sensitive and urlparse(current).netloc.lower() != initial_origin:
                raise ValueError("credentialed cross-origin redirect is forbidden")
            if response.status_code in {301, 302, 303} and method.upper() != "HEAD":
                method, kwargs = "GET", {}
        raise AssertionError("unreachable")

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)


requests = SafeRequests()
