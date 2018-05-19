import logging
import psutil
import shlex
import subprocess

from tunnel.db import Database

LOG = logging.getLogger(__name__)


class TunnelManager(object):
    def __init__(self):
        self.db = Database()

    def _run_ssh(self, cmd):
        args = shlex.split(cmd)
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            LOG.error("SSH not installed or not found in PATH")
            return

        try:
            out, err = proc.communicate(timeout=0.5)
            if proc.returncode != 0:
                LOG.err(err)
                return
        except Exception:
            LOG.debug("ssh still running")
        return proc.pid

    def create(self, server, port, local_port=None, name=None):
        if local_port is None:
            local_port = port

        if name is None:
            name = 'localhost'

        # TODO: check for in use

        ssh_cmd = "ssh -NL {local_port}:{name}:{remote_port} {server}".format(
            local_port=local_port,
            name=name,
            remote_port=port,
            server=server,
        )
        forward_name = "{} {}:{}".format(server, local_port, port)
        LOG.info("Starting tunnel {}".format(forward_name))
        pid = self._run_ssh(ssh_cmd)
        if pid is None:
            return

        self.db.create_tunnel(server, port, local_port, pid, name)

    def list(self):
        tunnels = self.db.list()
        if not tunnels:
            print('There are no tunnels.')
            return
        for i in range(len(tunnels)):
            pid, server, remote, local, name = tunnels[i]
            line = "{i}: {server} {local}:{remote}".format(
                i=i+1,
                server=server,
                local=local,
                remote=remote
            )
            print(line)

    def stop(self, num):
        tunnels = self.db.list()
        if num > len(tunnels) or num <= 0:
            LOG.error("Invalid number")
            print('There is no tunnel {}'.format(num))
            self.list()
            return
        tunnel = tunnels[num-1]
        pid = tunnel[0]
        try:
            p = psutil.Process(pid)
            if p.is_running():
                p.terminate()
                try:
                    p.wait(timeout=5)
                except psutil.TimeoutExpired:
                    p.kill()
        except psutil.NoSuchProcess:
            pass
        self.db.remove(pid)
