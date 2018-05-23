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

    def __eq__(self, other):
        if self is other:
            return True
        if type(other) != self.__class__:
            return False
        if self.server == other.server and \
           self.remote == other.remote and \
           self.local == other.local and \
           self.name == other.name:
            return True
        return False

    def _run_ssh(self, cmd):
        args = shlex.split(cmd)
        try:
            proc = subprocess.Popen(args,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except OSError:
            LOG.error("SSH not installed or not found in PATH")
            return

        try:
            out, err = proc.communicate(timeout=0.5)
            if proc.returncode != 0:
                LOG.err(err)
                return
        except Exception:
            pass
        return proc.pid

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

    def start(self):
        ssh_cmd = "ssh -NL {local}:{name}:{remote} {server}".format(
            local=self.local,
            name=self.name,
            remote=self.remote,
            server=self.server,
        )
        forward_name = "{} {}:{}".format(self.server, self.local, self.remote)
        LOG.info("Starting tunnel {}".format(forward_name))
        pid = self._run_ssh(ssh_cmd)
        if pid is None:
            return
        self.pid = pid

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
