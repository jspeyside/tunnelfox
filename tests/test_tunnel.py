import psutil
import subprocess

from mock import patch
from tests.base import BaseTest
from tunnel.tunnel import Tunnel

PROCS = {}


class MockProcess(object):
    terminate_time = 0
    terminate_called = False
    kill_called = False

    def __init__(self, pid, command):
        self.running = True
        self.pid = pid
        self.command = command

    def is_running(self):
        return self.running

    def kill(self):
        self.kill_called = True
        self.running = False

    def terminate(self):
        self.terminate_called = True
        if self.terminate_time > 0:
            return
        self.running = False

    def wait(self, timeout):
        print("running", self.running)
        print("timed out", timeout, self.terminate_time)
        if not self.running or self.terminate_time < timeout:
            return
        raise psutil.TimeoutExpired(
            "time to terminate {} exceeds timeout {}".format(self.terminate,
                                                             timeout))


class TestTunnel(BaseTest):
    def test_init(self):
        tunnel = Tunnel('host1', 8000, 8000, name='clown', pid=1234)
        assert tunnel.server == 'host1'
        assert tunnel.remote == 8000
        assert tunnel.local == 8000
        assert tunnel.name == 'clown'
        assert tunnel.pid == 1234

        tunnel2 = Tunnel('host2', 9000)
        assert tunnel2.server == 'host2'
        assert tunnel2.remote == 9000
        assert tunnel2.local == 9000
        assert tunnel2.name == 'localhost'
        assert tunnel2.pid is None

    def test_eq(self):
        tunnel = Tunnel('host1', 8080, 8080, pid=1234)
        tunnel2 = Tunnel('host2', 8180, 8180, pid=2345)
        tunnel3 = Tunnel('host1', 8080, 8080, pid=1234)
        assert tunnel == tunnel
        assert tunnel != tunnel2
        assert tunnel != list()
        assert tunnel == tunnel3

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
    @patch('tunnel.tunnel.subprocess.Popen')
    def test_start(self, mock_popen, mock_process):
        proc = MockProcess(2, 'ssh')
        mock_popen.return_value = proc
        mock_process.return_value = proc

        tunnel = Tunnel('host', 8080)
        tunnel.start()
        assert tunnel.is_alive()
        mock_popen.assert_called_once_with(
            ['ssh', '-NL', '8080:localhost:8080', 'host'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_process.assert_called()

    @patch('tunnel.tunnel.psutil.Process')
    def test_stop(self, mock_process):
        tunnel = Tunnel('server', 123, 456, pid=12345)
        proc = MockProcess(tunnel.pid, "ssh")
        mock_process.return_value = proc

        assert tunnel.is_alive()
        tunnel.stop()
        assert proc.terminate_called
        assert not proc.kill_called
        assert not tunnel.is_alive()

    @patch('tunnel.tunnel.psutil.Process')
    def test_stop_timeout(self, mock_process):
        tunnel = Tunnel('server', 123, 456, pid=12345)
        proc = MockProcess(tunnel.pid, "ssh")
        proc.running = True
        proc.terminate_time = 10
        mock_process.return_value = proc
        assert tunnel.is_alive()
        tunnel.stop()
        assert proc.terminate_called
        assert proc.kill_called
        assert not tunnel.is_alive()

    @patch('tunnel.tunnel.psutil.Process')
    def test_stop_no_proc(self, mock_process):
        tunnel = Tunnel('server', 123, 456, pid=12345)
        mock_process.side_effect = psutil.NoSuchProcess(tunnel.pid)
        tunnel.stop()
        assert not tunnel.is_alive()

    def test_stop_no_pid(self):
        tunnel = Tunnel('server', 123,)
        tunnel.stop()
        assert not tunnel.is_alive()
