"""RFC 8628 device-authorization flow against the Sophon auth service."""

from __future__ import annotations

import time
from typing import Any, Callable

from sophon_login import http
from sophon_login.errors import HTTPError, LoginDenied, LoginExpired

SLOW_DOWN_BACKOFF_SECONDS = 5


def start_device_flow(api_base_url: str) -> dict[str, Any]:
    return http.post_json(
        f"{api_base_url}/api/auth/device/start",
        {"client_name": "sophon-cli"},
    )


def poll_until_approved(
    *,
    api_base_url: str,
    device_code: str,
    interval: int,
    expires_in: int,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    deadline = now() + expires_in
    current_interval = interval
    while True:
        sleep(current_interval)
        if now() >= deadline:
            raise LoginExpired()
        try:
            return http.post_json(
                f"{api_base_url}/api/auth/device/poll",
                {"device_code": device_code},
            )
        except HTTPError as exc:
            code = exc.error_code()
            if code == "authorization_pending":
                continue
            if code == "slow_down":
                current_interval += SLOW_DOWN_BACKOFF_SECONDS
                continue
            if code == "expired_token":
                raise LoginExpired() from exc
            if code == "access_denied":
                raise LoginDenied() from exc
            raise
