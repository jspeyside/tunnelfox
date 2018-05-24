PIDS = 1


class MockDatabase(object):
    tunnels = None

    def __init__(self):
        self.tunnels = []

    def create_tunnel(self, tunnel):
        self.tunnels.append(tunnel)

    def close(self):
        pass

    def in_use(self, server, remote, local, name=None):
        if name is None:
            name = 'localhost'
        for t in self.tunnels:
            if t.server == server and \
               t.remote == remote and \
               t.local == local and \
               t.name == name:
                return True
        return False

    def list(self):
        return self.tunnels

    def reopen(self, tunnel):
        pass

    def remove(self, tunnel):
        for i in range(len(self.tunnels)):
            t = self.tunnels[i]
            if t == tunnel:
                del(self.tunnels[i])
                return


class MockTunnel(object):
    alive = False

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
        if self.server == other.server and \
           self.remote == other.remote and \
           self.local == other.local and \
           self.name == other.name:
            return True
        return False

    def is_alive(self):
        return self.alive

    def start(self):
        global PIDS
        PIDS += 1
        self.pid = PIDS
        self.alive = True

    def stop(self):
        self.alive = False
