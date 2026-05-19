"""Minimal JSON-over-HTTP POST helper backed by urllib."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from sophon_login.errors import HTTPError

HTTP_TIMEOUT_SECONDS = 10.0


def post_json(url: str, body: dict[str, Any], timeout: float = HTTP_TIMEOUT_SECONDS) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        raise HTTPError(status=exc.code, body=parsed) from exc
