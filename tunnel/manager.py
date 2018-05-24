import logging

from .db import Database
from .tunnel import Tunnel

LOG = logging.getLogger(__name__)


class TunnelManager(object):
    def __init__(self):
        self.db = Database()

    def create(self, server, port, local_port=None, name=None):
        if local_port is None:
            local_port = port

        if name is None:
            name = 'localhost'

        tunnel = Tunnel(server, port, local_port, name)
        # TODO: check for in use
        reopen = False
        for t in self.db.list():
            if tunnel == t:
                if t.is_alive():
                    print('Tunnel is already in use')
                    self.list()
                    return
                else:
                    print('reopening tunnel')
                    reopen = True
        tunnel.start()

        if reopen:
            self.db.reopen(tunnel)
            return

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
                i=(i + 1),
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
        tunnel = tunnels[num - 1]
        tunnel.stop()
        self.db.remove(tunnel)
