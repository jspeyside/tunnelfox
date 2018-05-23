import psutil

from mock import patch
from tests.base import BaseTest
from tunnel.tunnel import Tunnel

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


class TestTunnel(BaseTest):
    @patch('tunnel.tunnel.psutil.Process')
    def test_is_alive(self, mock_process):
        tunnel = Tunnel('server', 123, 456, pid=12345)
        proc = MockProcess(tunnel.pid, "ssh")
        mock_process.return_value = proc

        assert tunnel.is_alive()
        proc.running = False
        assert not tunnel.is_alive()
        proc.running = True
        mock_process.side_effect = psutil.NoSuchProcess(tunnel.pid)
        assert not tunnel.is_alive()

    @patch('tunnel.tunnel.psutil.Process')
    def test_stop(self, mock_process):
        tunnel = Tunnel('server', 123, 456, pid=12345)
        proc = MockProcess(tunnel.pid, "ssh")
        mock_process.return_value = proc

        assert tunnel.is_alive()
        tunnel.stop()
        assert not tunnel.is_alive()

    @patch('tunnel.tunnel.psutil.Process')
    def test_stop_timeout(self, mock_process):
        tunnel = Tunnel('server', 123, 456, pid=12345)
        proc = MockProcess(tunnel.pid, "ssh")
        proc.running = True
        proc.terminate_timeout = 10
        mock_process.return_value = proc
        assert tunnel.is_alive()
        tunnel.stop()
        assert not tunnel.is_alive()
