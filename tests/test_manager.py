from mock import patch

from tests.base import (
    capture_output,
    BaseTest,
)
from tests.mocks import (
    MockDatabase,
    MockTunnel,
)
from tunnel.manager import TunnelManager


class TestTunnelManager(BaseTest):
    @patch('tunnel.manager.Tunnel')
    @patch('tunnel.manager.Database')
    def test_create(self, mock_db, mock_tunnel):
        mock_db.return_value = MockDatabase()
        t = MockTunnel('host', 8080)
        t2 = MockTunnel('host2', 8080)
        mock_tunnel.return_value = t
        manager = TunnelManager()
        manager.create('host', 8080)
        mock_tunnel.return_value = t2
        manager.create('host2', 8080)
        assert t.is_alive()
        assert t in manager.db.list()
        assert t2.is_alive()
        assert t2 in manager.db.list()
        assert len(manager.db.list()) == 2

    @patch('tunnel.manager.Tunnel')
    @patch('tunnel.manager.Database')
    def test_create_in_use(self, mock_db, mock_tunnel):
        mock_db.return_value = MockDatabase()
        t = MockTunnel('host', 8080)
        mock_tunnel.return_value = t
        manager = TunnelManager()
        manager.create('host', 8080)
        with capture_output() as (out, err):
            manager.create('host', 8080)
        output = out.getvalue().strip()
        assert 'Tunnel is already in use' in output

    @patch('tunnel.manager.Tunnel')
    @patch('tunnel.manager.Database')
    def test_create_reopen(self, mock_db, mock_tunnel):
        mock_db.return_value = MockDatabase()
        t = MockTunnel('host', 8080)
        mock_tunnel.return_value = t
        manager = TunnelManager()
        manager.create('host', 8080)
        t.stop()
        with capture_output() as (out, err):
            manager.create('host', 8080)
        output = out.getvalue().strip()
        assert 'reopening tunnel' in output

    @patch('tunnel.manager.Tunnel')
    @patch('tunnel.manager.Database')
    def test_list(self, mock_db, mock_tunnel):
        mock_db.return_value = MockDatabase()
        t = MockTunnel('host', 8080)
        mock_tunnel.return_value = t
        manager = TunnelManager()
        manager.create('host', 8080)
        with capture_output() as (out, err):
            manager.list()
        output = out.getvalue().strip()
        assert '1: host 8080:8080' in output
        assert '1: host 8080:8080 (dead)' not in output
        t.stop()
        with capture_output() as (out, err):
            manager.list()
        output = out.getvalue().strip()
        assert '1: host 8080:8080 (dead)' in output

    @patch('tunnel.manager.Database')
    def test_list_empty(self, mock_db):
        mock_db.return_value = MockDatabase()
        manager = TunnelManager()
        with capture_output() as (out, err):
            manager.list()
        output = out.getvalue().strip()
        assert 'There are no tunnels.' in output

    @patch('tunnel.manager.Tunnel')
    @patch('tunnel.manager.Database')
    def test_stop(self, mock_db, mock_tunnel):
        mock_db.return_value = MockDatabase()
        t = MockTunnel('host', 8080)
        mock_tunnel.return_value = t
        manager = TunnelManager()
        manager.create('host', 8080)
        t2 = MockTunnel('host2', 8080)
        mock_tunnel.return_value = t2
        manager.create('host2', 8080)
        with capture_output() as (out, err):
            manager.list()
        output = out.getvalue().strip()
        assert '1: host 8080:8080' in output
        assert '2: host2 8080:8080' in output
        assert t in manager.db.list()
        assert t2 in manager.db.list()
        manager.stop(2)
        assert t in manager.db.list()
        assert t2 not in manager.db.list()

    @patch('tunnel.manager.Tunnel')
    @patch('tunnel.manager.Database')
    def test_stop_invalid(self, mock_db, mock_tunnel):
        mock_db.return_value = MockDatabase()
        t = MockTunnel('host', 8080)
        mock_tunnel.return_value = t
        manager = TunnelManager()
        manager.create('host', 8080)
        t2 = MockTunnel('host2', 8080)
        mock_tunnel.return_value = t2
        manager.create('host2', 8080)
        with capture_output() as (out, err):
            manager.list()
        output = out.getvalue().strip()
        assert '1: host 8080:8080' in output
        assert '2: host2 8080:8080' in output
        assert t in manager.db.list()
        assert t2 in manager.db.list()
        with capture_output() as (out, err):
            manager.stop(-5)
        output = out.getvalue().strip()
        assert 'There is no tunnel -5' in output

    @patch('tunnel.manager.Tunnel')
    @patch('tunnel.manager.Database')
    def test_stop_invalid2(self, mock_db, mock_tunnel):
        mock_db.return_value = MockDatabase()
        t = MockTunnel('host', 8080)
        mock_tunnel.return_value = t
        manager = TunnelManager()
        manager.create('host', 8080)
        t2 = MockTunnel('host2', 8080)
        mock_tunnel.return_value = t2
        manager.create('host2', 8080)
        with capture_output() as (out, err):
            manager.list()
        output = out.getvalue().strip()
        assert '1: host 8080:8080' in output
        assert '2: host2 8080:8080' in output
        assert t in manager.db.list()
        assert t2 in manager.db.list()
        with capture_output() as (out, err):
            manager.stop(3)
        output = out.getvalue().strip()
        assert 'There is no tunnel 3' in output
