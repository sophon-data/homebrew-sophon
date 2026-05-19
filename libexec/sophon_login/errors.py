"""Exceptions raised by the device-code login client."""

from __future__ import annotations

from typing import Any


class HTTPError(Exception):
    """An HTTP non-2xx response from the auth service."""

    def __init__(self, *, status: int, body: dict[str, Any] | None) -> None:
        self.status = status
        self.body = body or {}
        super().__init__(f"HTTP {status}: {body}")

    def error_code(self) -> str | None:
        detail = self.body.get("detail")
        if isinstance(detail, dict) and "error" in detail:
            return str(detail["error"])
        if "error" in self.body:
            return str(self.body["error"])
        return None


class LoginExpired(Exception):
    pass


class LoginDenied(Exception):
    pass
