from mock import patch
from tests.base import (
    capture_output,
    BaseTest,
)
from tunnel.manager import TunnelManager


class TestTunnelManager(BaseTest):
    @patch('tunnel.manager.Database')
    def test_list(self, mock_db):
        manager = TunnelManager()
        manager.db.list.return_value = []
        manager.list()
        with capture_output() as (out, err):
            manager.list()
        output = out.getvalue().strip()
        manager.db.list.assert_called()
        assert 'There are no tunnels.' in output
