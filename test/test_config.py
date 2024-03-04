import sys
import unittest
from pathlib import Path
import json
from tempfile import gettempdir
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))
from toggl2github.config import set_config, get_config  # noqa
from toggl2github.config import CONFIG_FILE as ORIG_CONFIG_FILE  # noqa

CONFIG_FILE = Path(gettempdir()) / ORIG_CONFIG_FILE.name


class TestSetConfig(unittest.TestCase):

    @patch('toggl2github.config.CONFIG_FILE', CONFIG_FILE)
    def setUp(self) -> None:

        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()

    @patch('toggl2github.config.keyring.set_password')
    @patch('toggl2github.config.CONFIG_FILE', CONFIG_FILE)
    def test_set_config_with_password(self, mock_set_password: MagicMock):

        kwargs = {
            'user_1': 'test_user1',
            'password_1': 'test_password1',
        }
        set_config(**kwargs)

        mock_set_password.assert_called_with(service_name='toggl2github.password_1', 
                                             username='test_user1', 
                                             password='test_password1')
        self.assertTrue(CONFIG_FILE.exists())
        self.assertDictEqual({k: v for k, v in kwargs.items() if 'password' not in k},
                             json.loads(CONFIG_FILE.read_text()))

    @patch('toggl2github.config.keyring.set_password')
    @patch('toggl2github.config.CONFIG_FILE', CONFIG_FILE)
    def test_set_config_without_password(self, mock_set_password: MagicMock):
        kwargs = {
            'user': 'test_user',
            'key1': 'value1',
            'key2': 'value2'
        }
        set_config(**kwargs)
        mock_set_password.assert_not_called()
        self.assertTrue(CONFIG_FILE.exists())
        self.assertDictEqual({k: v for k, v in kwargs.items() if 'password' not in k},
                             json.loads(CONFIG_FILE.read_text()))

    def tearDown(self) -> None:

        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()


class TestGetConfig(unittest.TestCase):

    SETTINGS = {
        'user': 'test_user',
        'key1': 'value1',
        'key2': 'value2'
    }

    @patch('toggl2github.config.CONFIG_FILE', CONFIG_FILE)
    def setUp(self) -> None:

        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()

        set_config(**self.SETTINGS)

    @patch('toggl2github.config.CONFIG_FILE', CONFIG_FILE)
    def test_get_config(self):

        config = get_config(list(self.SETTINGS))
        self.assertDictEqual(self.SETTINGS, config)

    def tearDown(self) -> None:

        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
