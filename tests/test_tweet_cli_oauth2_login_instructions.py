import sys
import unittest
from unittest import mock

from birdapp import main as main_module


class TestTweetCliOAuth2LoginInstructions(unittest.TestCase):
    def test_tweet_when_oauth2_configured_but_not_logged_in_instructs_oauth2_login(self) -> None:
        """
        When OAuth2 app credentials are configured but no OAuth2 token is stored
        for the selected profile, the user should be instructed to run the OAuth2
        login flow (not OAuth1 configuration).
        """
        with (
            mock.patch.object(sys, "argv", ["birdapp", "tweet", "hello"]),
            mock.patch("birdapp.main._has_oauth2_config", return_value=True),
            mock.patch("birdapp.main.has_oauth2_token", return_value=False),
            mock.patch("birdapp.main._has_oauth1_credentials", return_value=False),
            mock.patch("birdapp.main.post_tweet") as post_tweet,
            mock.patch("builtins.print") as print_mock,
        ):
            main_module.main()

        post_tweet.assert_not_called()
        printed = "\n".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        self.assertIn("auth login", printed)
        self.assertNotIn("--oauth1", printed)
        self.assertNotIn("Missing required credentials", printed)

