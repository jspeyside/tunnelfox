import pytest
from mock import (
    patch,
    Mock,
)
from tests.base import BaseTest
from tunnel import main


class TestDatabase(BaseTest):
    def setup_method(self, test_method):
        print("SETUP")
        self.patcher = patch('tunnel.TunnelManager', autospec=True)
        self.mock_manager = Mock()
        self.patcher.start().return_value = self.mock_manager
        # self.mock_manager.list

    def teardown_method(self):
        print("TEARDOWN")
        self.patcher.stop()

    @patch('tunnel.sys.argv', ['tunnelfox', 'ls'])
    def test_list(self):
        main()
        self.mock_manager.list.assert_called_once()

    @patch('tunnel.sys.argv', ['tunnelfox', 'new', '-s', 'host', '-p', '8080'])
    def test_create(self):
        main()
        self.mock_manager.create.assert_called_once_with(
            'host', 8080, None, None)

    @patch('tunnel.sys.argv', ['tunnelfox', 'stop', '1'])
    def test_stop(self):
        main()
        self.mock_manager.stop.assert_called_once_with(1)

    @patch('tunnel.sys.argv', ['tunnelfox'])
    def test_no_args(self):
        with pytest.raises(SystemExit):
            main()
