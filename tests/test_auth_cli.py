import sys
import unittest
from unittest import mock

from birdapp import main as main_module


class TestAuthCli(unittest.TestCase):
    def test_auth_config_oauth2_flag_calls_prompt(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "config", "--oauth2"]),
            mock.patch("birdapp.main.prompt_for_oauth2_credentials") as oauth2_prompt,
            mock.patch("birdapp.main.prompt_for_credentials") as oauth1_prompt,
        ):
            main_module.main()

        oauth2_prompt.assert_called_once()
        oauth1_prompt.assert_not_called()

    def test_auth_config_show_calls_show_config(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "config", "--show"]),
            mock.patch("birdapp.main.show_config") as show_config,
        ):
            main_module.main()

        show_config.assert_called_once()

    def test_auth_config_show_with_profile_calls_show_config(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "--profile", "alice", "auth", "config", "--show"]),
            mock.patch("birdapp.main.show_config") as show_config,
        ):
            main_module.main()

        show_config.assert_called_once_with(profile="alice")

    def test_auth_config_prompts_for_flow(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "config"]),
            mock.patch("builtins.input", return_value="oauth2"),
            mock.patch("birdapp.main.prompt_for_oauth2_credentials") as oauth2_prompt,
        ):
            main_module.main()

        oauth2_prompt.assert_called_once()

    def test_auth_login_requires_oauth2_config(self) -> None:
        def fake_get_credential(key: str) -> str | None:
            return None

        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "login"]),
            mock.patch("birdapp.main.get_credential", side_effect=fake_get_credential),
            mock.patch("birdapp.main.os.getenv", return_value=None),
            mock.patch("birdapp.main.oauth2_login_flow") as oauth2_login_flow,
            mock.patch("builtins.print") as print_mock,
        ):
            main_module.main()

        oauth2_login_flow.assert_not_called()
        printed = " ".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        self.assertIn("OAuth2 credentials are not configured", printed)

    def test_auth_login_skips_when_oauth1_configured(self) -> None:
        def fake_get_credential(key: str) -> str | None:
            oauth1_values = {
                "X_API_KEY": "key",
                "X_API_SECRET": "secret",
                "X_ACCESS_TOKEN": "token",
                "X_ACCESS_TOKEN_SECRET": "token-secret",
            }
            return oauth1_values.get(key)

        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "login"]),
            mock.patch("birdapp.main.get_credential", side_effect=fake_get_credential),
            mock.patch("birdapp.main.os.getenv", return_value=None),
            mock.patch("birdapp.main.oauth2_login_flow") as oauth2_login_flow,
            mock.patch("builtins.print") as print_mock,
        ):
            main_module.main()

        oauth2_login_flow.assert_not_called()
        printed = " ".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        self.assertIn("OAuth1 credentials are configured", printed)

    def test_auth_login_runs_oauth2_flow(self) -> None:
        def fake_get_credential(key: str) -> str | None:
            oauth2_values = {
                "X_OAUTH2_CLIENT_ID": "client",
                "X_OAUTH2_REDIRECT_URI": "http://127.0.0.1:8080/callback",
            }
            return oauth2_values.get(key)

        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "login"]),
            mock.patch("birdapp.main.get_credential", side_effect=fake_get_credential),
            mock.patch("birdapp.main.os.getenv", return_value=None),
            mock.patch("birdapp.main.oauth2_login_flow", return_value={"data": {"id": "1"}})
            as oauth2_login_flow,
        ):
            main_module.main()

        oauth2_login_flow.assert_called_once()

    def test_auth_login_passes_profile_override(self) -> None:
        def fake_get_credential(key: str) -> str | None:
            oauth2_values = {
                "X_OAUTH2_CLIENT_ID": "client",
                "X_OAUTH2_REDIRECT_URI": "http://127.0.0.1:8080/callback",
            }
            return oauth2_values.get(key)

        with (
            mock.patch.object(sys, "argv", ["birdapp", "--profile", "alice", "auth", "login"]),
            mock.patch("birdapp.main.get_credential", side_effect=fake_get_credential),
            mock.patch("birdapp.main.os.getenv", return_value=None),
            mock.patch("birdapp.main.oauth2_login_flow", return_value={"data": {"id": "1"}})
            as oauth2_login_flow,
        ):
            main_module.main()

        oauth2_login_flow.assert_called_once_with(profile="alice")

    def test_auth_whoami_calls_oauth2_whoami(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "auth", "whoami"]),
            mock.patch("birdapp.main.oauth2_whoami", return_value={"data": {"id": "1"}})
            as oauth2_whoami,
        ):
            main_module.main()

        oauth2_whoami.assert_called_once()

    def test_profile_use_sets_active_profile(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "profile", "use", "alice"]),
            mock.patch("birdapp.main.has_profile", return_value=True),
            mock.patch("birdapp.main.set_active_profile") as set_active_profile,
        ):
            main_module.main()

        set_active_profile.assert_called_once_with("alice")
