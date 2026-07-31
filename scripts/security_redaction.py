"""Recursive secret redaction for logs and diagnostic JSON."""

from __future__ import annotations

import re
from typing import Any


SECRET_KEY = re.compile(
    r"(authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|"
    r"client[_-]?secret|password|private[_-]?key)",
    re.IGNORECASE,
)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if SECRET_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    if isinstance(value, str):
        return re.sub(
            r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+",
            r"\1 [REDACTED]",
            value,
        )
    return value
