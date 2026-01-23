from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from unittest import mock

from birdapp import main as main_module
from birdapp.storage.embeddings import EmbeddingsUnavailable
from birdapp.storage.search import SearchOwner, SearchResult


class TestSearchCli(unittest.TestCase):
    def test_search_cli_emits_json_results(self) -> None:
        sample_results = [
            SearchResult(
                tweet_id="111",
                created_at=datetime(2023, 5, 1, tzinfo=timezone.utc),
                full_text="hello",
                tweet_kind="tweet",
                owner=SearchOwner(
                    account_id="42",
                    username="alice",
                    account_display_name="Alice",
                ),
                rank=0.1,
            )
        ]
        with (
            mock.patch.object(
                sys,
                "argv",
                ["birdapp", "search", "hello", "--db", "sqlite:///:memory:", "--json"],
            ),
            mock.patch("birdapp.main.search_tweets_in_db", return_value=sample_results),
            mock.patch("builtins.print") as print_mock,
        ):
            main_module.main()

        printed = " ".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        payload = json.loads(printed)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["tweet_id"], "111")
        self.assertEqual(payload["results"][0]["owner"]["username"], "alice")

    def test_search_cli_semantic_handles_missing_embeddings(self) -> None:
        with (
            mock.patch.object(
                sys,
                "argv",
                ["birdapp", "search", "hello", "--semantic"],
            ),
            mock.patch(
                "birdapp.main.semantic_search_tweets_in_db",
                side_effect=EmbeddingsUnavailable(
                    'No embeddings found. Run "birdapp embed" first.'
                ),
            ),
            mock.patch("builtins.print") as print_mock,
        ):
            main_module.main()

        printed = " ".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
        self.assertIn('No embeddings found. Run "birdapp embed" first.', printed)
