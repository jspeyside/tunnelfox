import logging
import psutil

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
