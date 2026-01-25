import unittest
from unittest import mock

from birdapp.oauth2 import DEFAULT_OAUTH2_SCOPES


class TestConfigShowOAuth2Scopes(unittest.TestCase):
    def test_show_config_prints_default_oauth2_scopes_when_not_explicitly_set(self) -> None:
        config = {
            "active_profile": "WSPZoo",
            "profiles": {"WSPZoo": {"X_USERNAME": "WSPZoo"}},
            "oauth2_app": {
                "X_OAUTH2_CLIENT_ID": "client-id",
                "X_OAUTH2_CLIENT_SECRET": "client-secret",
                "X_OAUTH2_REDIRECT_URI": "http://127.0.0.1:5000/oauth/callback",
                # X_OAUTH2_SCOPES intentionally omitted -> defaults should be used.
            },
        }

        with (
            mock.patch("birdapp.config.load_config", return_value=config),
            mock.patch("builtins.print") as print_mock,
        ):
            from birdapp import config as config_module

            config_module.show_config()

        printed = "\n".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        self.assertIn(f"OAuth2 Scopes: Default ({DEFAULT_OAUTH2_SCOPES})", printed)
        self.assertNotIn("OAuth2 Scopes: Not set", printed)
        self.assertEqual(printed.count("OAuth2 Scopes:"), 1)

    def test_show_config_prints_explicit_oauth2_scopes_when_set(self) -> None:
        config = {
            "active_profile": "WSPZoo",
            "profiles": {"WSPZoo": {"X_USERNAME": "WSPZoo"}},
            "oauth2_app": {
                "X_OAUTH2_CLIENT_ID": "client-id",
                "X_OAUTH2_CLIENT_SECRET": "client-secret",
                "X_OAUTH2_REDIRECT_URI": "http://127.0.0.1:5000/oauth/callback",
                "X_OAUTH2_SCOPES": "tweet.read users.read",
            },
        }

        with (
            mock.patch("birdapp.config.load_config", return_value=config),
            mock.patch("builtins.print") as print_mock,
        ):
            from birdapp import config as config_module

            config_module.show_config()

        printed = "\n".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        self.assertIn("OAuth2 Scopes: tweet.read users.read", printed)
        self.assertNotIn(f"OAuth2 Scopes: Default ({DEFAULT_OAUTH2_SCOPES})", printed)
        self.assertEqual(printed.count("OAuth2 Scopes:"), 1)

