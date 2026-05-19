"""User-facing CLI commands: `sophon login`, `sophon logout`."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import webbrowser
from datetime import datetime, timedelta, timezone
from typing import Any

from sophon_login import config as config_mod
from sophon_login import device_flow
from sophon_login.errors import HTTPError, LoginDenied, LoginExpired


def _print_verification_instructions(start: dict[str, Any]) -> None:
    sys.stdout.write(
        "\n"
        "To finish signing in, visit:\n"
        f"  {start['verification_uri']}\n\n"
        "And enter the code:\n"
        f"  {start['user_code']}\n\n"
        "Or open this URL directly:\n"
        f"  {start['verification_uri_complete']}\n\n"
        "Waiting for approval... (Ctrl-C to cancel)\n"
    )
    sys.stdout.flush()


def _open_browser(url: str) -> None:
    try:
        webbrowser.open(url, new=2)
    except Exception:
        pass


def cmd_login(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="sophon login")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser")
    args = parser.parse_args(argv)

    api_base = config_mod.api_base_url()
    try:
        start = device_flow.start_device_flow(api_base)
    except HTTPError as exc:
        sys.stderr.write(f"sophon: device/start failed (HTTP {exc.status}): {exc.body}\n")
        return 1
    except urllib.error.URLError as exc:
        sys.stderr.write(
            f"sophon: cannot reach {api_base} ({exc.reason}). "
            "Set SOPHON_API_BASE_URL or start the local backend.\n"
        )
        return 1

    _print_verification_instructions(start)
    if not args.no_browser:
        _open_browser(start["verification_uri_complete"])

    try:
        poll = device_flow.poll_until_approved(
            api_base_url=api_base,
            device_code=start["device_code"],
            interval=int(start["interval"]),
            expires_in=int(start["expires_in"]),
        )
    except LoginExpired:
        sys.stderr.write("sophon: code expired before approval. Run `sophon login` again.\n")
        return 1
    except LoginDenied:
        sys.stderr.write("sophon: login was denied.\n")
        return 1
    except urllib.error.URLError as exc:
        sys.stderr.write(f"sophon: network error while polling: {exc.reason}\n")
        return 1

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(poll["expires_in"]))
    path = config_mod.config_path()
    config_mod.write_config(
        config_path=path,
        token=poll["access_token"],
        expires_at_iso=expires_at.isoformat(),
        api_base_url=api_base,
    )
    sys.stdout.write(f"sophon: signed in. Token written to {path}\n")
    return 0


def cmd_logout(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="sophon logout")
    parser.parse_args(argv)
    path = config_mod.config_path()
    config_mod.clear_config(config_path=path)
    sys.stdout.write(f"sophon: signed out. Cleared {path}\n")
    return 0
