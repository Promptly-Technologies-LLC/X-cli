import sys
import unittest
from unittest import mock

from birdapp import main as main_module


class TestTweetCli(unittest.TestCase):
    def test_tweet_cli_accepts_positional_text(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "tweet", "hello world"]),
            mock.patch("birdapp.main.post_tweet", return_value=(True, "ok")) as post_tweet,
            mock.patch("builtins.print"),
        ):
            main_module.main()

        post_tweet.assert_called_once_with(text="hello world", media_path=None, reply_to=None)

    def test_tweet_cli_still_accepts_text_flag(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["birdapp", "tweet", "--text", "hello world"]),
            mock.patch("birdapp.main.post_tweet", return_value=(True, "ok")) as post_tweet,
            mock.patch("builtins.print"),
        ):
            main_module.main()

        post_tweet.assert_called_once_with(text="hello world", media_path=None, reply_to=None)

