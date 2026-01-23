from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from birdapp import main as main_module
from birdapp.storage.embeddings import resolve_embedding_config


class TestEmbeddingsConfigCli(unittest.TestCase):
    def test_embed_config_writes_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            with (
                mock.patch("birdapp.config.get_config_path", return_value=config_path),
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        "birdapp",
                        "embed",
                        "config",
                        "--api-key",
                        "sk-test",
                        "--model",
                        "text-embedding-3-small",
                    ],
                ),
            ):
                main_module.main()

            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["embeddings"]["OPENAI_API_KEY"], "sk-test")
            self.assertEqual(
                config["embeddings"]["BIRDAPP_EMBEDDING_MODEL"],
                "text-embedding-3-small",
            )

    def test_embed_config_show_redacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "embeddings": {
                            "OPENAI_API_KEY": "sk-test",
                            "BIRDAPP_EMBEDDING_MODEL": "text-embedding-3-small",
                        }
                    }
                ),
                encoding="utf-8",
            )
            with (
                mock.patch("birdapp.config.get_config_path", return_value=config_path),
                mock.patch.object(
                    sys,
                    "argv",
                    ["birdapp", "embed", "config", "--show"],
                ),
                mock.patch("builtins.print") as print_mock,
            ):
                main_module.main()

            printed = " ".join(" ".join(map(str, args)) for args, _ in print_mock.call_args_list)
            self.assertIn("Embedding configuration", printed)
            self.assertIn("OPENAI_API_KEY: ****", printed)
            self.assertIn("BIRDAPP_EMBEDDING_MODEL: text-embedding-3-small", printed)

    def test_resolve_embedding_config_uses_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "embeddings": {
                            "OPENAI_API_KEY": "sk-test",
                            "BIRDAPP_EMBEDDING_MODEL": "text-embedding-3-small",
                        }
                    }
                ),
                encoding="utf-8",
            )
            with (
                mock.patch("birdapp.config.get_config_path", return_value=config_path),
                mock.patch("birdapp.storage.embeddings.os.getenv", return_value=None),
            ):
                config = resolve_embedding_config(model_override=None)

        self.assertEqual(config.api_key, "sk-test")
        self.assertEqual(config.model, "text-embedding-3-small")
