"""On-disk credential store for the Sophon CLI: ~/.sophon/config.toml."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_API_BASE_URL = "http://localhost:8001"
DEFAULT_CONFIG_PATH = Path.home() / ".sophon" / "config.toml"


def api_base_url() -> str:
    return os.environ.get("SOPHON_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


def config_path() -> Path:
    override = os.environ.get("SOPHON_CONFIG_PATH")
    return Path(override) if override else DEFAULT_CONFIG_PATH


def write_config(
    *,
    config_path: Path,
    token: str,
    expires_at_iso: str,
    api_base_url: str,
) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(config_path.parent, 0o700)
    body = (
        "[auth]\n"
        f'token = "{token}"\n'
        f'expires_at = "{expires_at_iso}"\n'
        f'api_base_url = "{api_base_url}"\n'
    )
    fd = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(body)
    os.chmod(config_path, 0o600)


def clear_config(*, config_path: Path) -> None:
    if config_path.exists():
        config_path.unlink()
