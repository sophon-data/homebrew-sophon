import os
import stat
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import conftest  # noqa: F401

from sophon_login.config import clear_config, write_config


class WriteConfigTests(unittest.TestCase):
    def test_writes_toml_with_expected_keys(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "config.toml"
            write_config(
                config_path=cfg,
                token="jwt-token",
                expires_at_iso="2026-06-19T00:00:00+00:00",
                api_base_url="http://api.example.com",
            )
            content = cfg.read_text()
        self.assertIn("[auth]", content)
        self.assertIn('token = "jwt-token"', content)
        self.assertIn('expires_at = "2026-06-19T00:00:00+00:00"', content)
        self.assertIn('api_base_url = "http://api.example.com"', content)

    def test_file_perms_0600(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "config.toml"
            write_config(
                config_path=cfg,
                token="t",
                expires_at_iso="2026-06-19T00:00:00+00:00",
                api_base_url="http://api",
            )
            mode = stat.S_IMODE(cfg.stat().st_mode)
        self.assertEqual(mode, 0o600)

    def test_creates_parent_dir_with_0700(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "nested" / "config.toml"
            write_config(
                config_path=cfg,
                token="t",
                expires_at_iso="2026-06-19T00:00:00+00:00",
                api_base_url="http://api",
            )
            parent_mode = stat.S_IMODE(cfg.parent.stat().st_mode)
        self.assertEqual(parent_mode, 0o700)

    def test_overwrites_existing_file(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "config.toml"
            cfg.write_text("garbage")
            write_config(
                config_path=cfg,
                token="new",
                expires_at_iso="2026-06-19T00:00:00+00:00",
                api_base_url="http://api",
            )
            content = cfg.read_text()
        self.assertNotIn("garbage", content)
        self.assertIn('token = "new"', content)


class ClearConfigTests(unittest.TestCase):
    def test_removes_existing(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "config.toml"
            cfg.write_text("anything")
            clear_config(config_path=cfg)
            self.assertFalse(cfg.exists())

    def test_no_op_when_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "config.toml"
            clear_config(config_path=cfg)


if __name__ == "__main__":
    unittest.main()
