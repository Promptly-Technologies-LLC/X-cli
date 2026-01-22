import sys
import unittest
from unittest import mock

from x_cli import main as main_module


class TestImportArchiveCli(unittest.TestCase):
    def test_import_archive_defaults_username_from_config(self) -> None:
        with (
            mock.patch.object(sys, "argv", ["x-cli", "import-archive"]),
            mock.patch("x_cli.main.import_archive") as import_archive_mock,
            mock.patch("x_cli.main.get_credential") as get_credential_mock,
        ):
            get_credential_mock.return_value = "configuser"
            import_archive_mock.return_value = {"tweet": 0}

            main_module.main()

            import_archive_mock.assert_called_once()
            _, kwargs = import_archive_mock.call_args
            self.assertEqual(kwargs["username"], "configuser")
