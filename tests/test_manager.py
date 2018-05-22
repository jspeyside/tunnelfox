import psutil

from mock import (
    patch,
    Mock,
    MagicMock,
)
from tests.base import (
    capture_output,
    BaseTest,
)
from tunnel.manager import TunnelManager
from tunnel.tunnel import Tunnel
from tunnel.db import Database

PROCS = {}


class MockProcess(object):
    terminate_time = 0

    def __init__(self, pid, command):
        self.running = True
        self.pid = pid
        self.command = command

    def is_running(self):
        return self.running

    def kill(self):
        self.running = False

    def terminate(self):
        if self.terminate_time > 0:
            return
        self.running = False

    def wait(self, timeout):
        if not self.running or timeout < self.terminate_time:
            return
        raise psutil.TimeoutExpired()


class TestTunnelManager(BaseTest):
    def setUp(self):
        print("SETUP TEST")

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
