import logging
import os
import sqlite3

from tunnel.manager import Tunnel


LOG = logging.getLogger(__name__)
HOME = os.path.expanduser("~")
TUNNELFOX_PATH = os.path.join(HOME, ".tunnelfox")


class Database(object):
    def __init__(self):
        if not os.path.exists(TUNNELFOX_PATH):
            LOG.debug("Creating tunnelfox path")
            os.mkdir(TUNNELFOX_PATH)
        db = os.path.join(TUNNELFOX_PATH, 'tunnelfox.db')
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()

        # Create the schema
        self._schema()

    def _schema(self):
        # Tunnels
        sql = "CREATE TABLE IF NOT EXISTS tunnel (server text, remote integer, local integer, name text, pid integer)"
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # def create_tunnel(self, server, remote, local, pid, name=None):
    def create_tunnel(self, tunnel):
        if tunnel.pid is None:
            raise Exception("pid is required")
        sql = "INSERT INTO tunnel VALUES('{server}', {remote}, {local}, '{name}', {pid})".format(
            server=tunnel.server,
            remote=tunnel.remote,
            local=tunnel.local,
            pid=tunnel.pid,
            name=tunnel.name,
        )
        self.cursor.execute(sql)
        self.conn.commit()

    def in_use(self, server, remote, local, name=None):
        if name is None:
            name = 'localhost'
        params = (server, remote, local, name)
        self.cursor.execute('SELECT * FROM tunnel WHERE server=? AND remote=? AND local=? AND name=?', params)
        tunnel = self.cursor.fetchone()
        if tunnel is None:
            return False
        return True

    def list(self):
        self.cursor.execute('SELECT * FROM tunnel')
        rows = self.cursor.fetchall()
        tunnels = []
        for row in rows:
            tunnels.append(Tunnel(*row))
        return tunnels

    def remove(self, tunnel):
        sql = "DELETE FROM tunnel WHERE pid=?"
        self.cursor.execute(sql, (tunnel.pid,))
        self.conn.commit()
