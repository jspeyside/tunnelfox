import logging
import psutil
import shlex
import subprocess

LOG = logging.getLogger(__name__)


class Tunnel(object):
    def __init__(self, server, remote, local=None, name=None, pid=None):
        self.server = server
        self.remote = remote

        if local is None:
            local = remote
        if name is None:
            name = 'localhost'
        self.local = local
        self.name = name
        self.pid = pid

    def is_alive(self):
        if self.pid is None:
            return False
        try:
            p = psutil.Process(int(self.pid))
        except psutil.NoSuchProcess:
            return False
        if not p.is_running():
            return False
        return True

    def stop(self):
        if self.pid is None:
            return
        try:
            p = psutil.Process(self.pid)
            if p.is_running():
                p.terminate()
                try:
                    p.wait(timeout=5)
                except psutil.TimeoutExpired:
                    p.kill()
        except psutil.NoSuchProcess:
            return


class TunnelManager(object):
    def __init__(self):
        from tunnel.db import Database
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

        tunnel = Tunnel(server, port, local_port, name)

        # TODO: check for in use
        # existing = self.db.list()
        # for e in existing:
        #     e_s
        #     if server == e.server and
        #        port == e.port and
        #        local_port == e.

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
        tunnel.pid = pid

        self.db.create_tunnel(tunnel)

    def list(self):
        tunnels = self.db.list()
        if not tunnels:
            print('There are no tunnels.')
            return
        for i in range(len(tunnels)):
            tunnel = tunnels[i]
            if tunnel.is_alive():
                alive_msg = ''
            else:
                alive_msg = ' (dead)'
            line = "{i}: {server} {local}:{remote}{alive_msg}".format(
                i=i+1,
                server=tunnel.server,
                local=tunnel.local,
                remote=tunnel.remote,
                alive_msg=alive_msg,
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
        tunnel.stop()
        self.db.remove(tunnel)
