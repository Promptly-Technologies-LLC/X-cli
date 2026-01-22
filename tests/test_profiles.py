import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from birdapp import config as config_module


class TestProfiles(unittest.TestCase):
    def _write_config(self, tmpdir: str, data: dict) -> Path:
        config_dir = Path(tmpdir) / ".config" / "birdapp"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.json"
        config_path.write_text(json.dumps(data))
        return config_path

    def test_get_credential_uses_active_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "active_profile": "alice",
                "profiles": {
                    "alice": {"X_API_KEY": "alice-key"},
                    "bob": {"X_API_KEY": "bob-key"},
                },
            }
            self._write_config(tmpdir, data)
            with mock.patch.object(config_module.Path, "home", return_value=Path(tmpdir)):
                self.assertEqual(config_module.get_credential("X_API_KEY"), "alice-key")
                self.assertEqual(
                    config_module.get_credential("X_API_KEY", profile="bob"),
                    "bob-key",
                )

    def test_get_credential_legacy_config_still_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {"X_API_KEY": "legacy-key", "X_USERNAME": "legacy-user"}
            self._write_config(tmpdir, data)
            with mock.patch.object(config_module.Path, "home", return_value=Path(tmpdir)):
                self.assertEqual(config_module.get_credential("X_API_KEY"), "legacy-key")

    def test_set_active_profile_updates_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "active_profile": "alice",
                "profiles": {"alice": {"X_API_KEY": "alice-key"}, "bob": {"X_API_KEY": "bob-key"}},
            }
            self._write_config(tmpdir, data)
            with mock.patch.object(config_module.Path, "home", return_value=Path(tmpdir)):
                config_module.set_active_profile("bob")
                config_path = config_module.get_config_path()
                updated = json.loads(config_path.read_text())
                self.assertEqual(updated["active_profile"], "bob")

    def test_profile_override_takes_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "active_profile": "alice",
                "profiles": {
                    "alice": {"X_API_KEY": "alice-key"},
                    "bob": {"X_API_KEY": "bob-key"},
                },
            }
            self._write_config(tmpdir, data)
            with mock.patch.object(config_module.Path, "home", return_value=Path(tmpdir)):
                config_module.set_profile_override("bob")
                try:
                    self.assertEqual(config_module.get_credential("X_API_KEY"), "bob-key")
                finally:
                    config_module.clear_profile_override()

    def test_oauth2_app_credentials_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "profiles": {"alice": {"X_USERNAME": "alice"}},
                "oauth2_app": {"X_OAUTH2_CLIENT_ID": "client-123"},
            }
            self._write_config(tmpdir, data)
            with mock.patch.object(config_module.Path, "home", return_value=Path(tmpdir)):
                self.assertEqual(
                    config_module.get_credential("X_OAUTH2_CLIENT_ID", profile="alice"),
                    "client-123",
                )

    def test_prompt_for_oauth2_credentials_saves_app_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_config(tmpdir, {})
            with (
                mock.patch.object(config_module.Path, "home", return_value=Path(tmpdir)),
                mock.patch("builtins.input", side_effect=["client-id", "http://127.0.0.1/callback", ""]),
                mock.patch("getpass.getpass", return_value=""),
            ):
                config_module.prompt_for_oauth2_credentials()
                config = config_module.load_config()

            self.assertIn("oauth2_app", config)
            self.assertEqual(config["oauth2_app"]["X_OAUTH2_CLIENT_ID"], "client-id")

    def test_ensure_profile_creates_and_sets_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_config(tmpdir, {})
            with mock.patch.object(config_module.Path, "home", return_value=Path(tmpdir)):
                config_module.ensure_profile("alice")
                config = config_module.load_config()

            self.assertEqual(config.get("active_profile"), "alice")
            self.assertIn("profiles", config)
            self.assertEqual(config["profiles"]["alice"]["X_USERNAME"], "alice")
