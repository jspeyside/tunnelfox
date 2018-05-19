import logging
import os
import sqlite3

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
        sql = "CREATE TABLE IF NOT EXISTS tunnel (pid integer, server text, remote integer, local integer, name text)"
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def create_tunnel(self, server, remote, local, pid, name=None):
        if name is None:
            name = 'localhost'
        sql = "INSERT INTO tunnel VALUES({pid}, '{server}', {remote}, {local}, '{name}')".format(
            server=server,
            remote=remote,
            local=local,
            pid=pid,
            name=name,
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
        tunnels = self.cursor.fetchall()
        return tunnels

    def remove(self, pid):
        sql = "DELETE FROM tunnel WHERE pid=?"
        self.cursor.execute(sql, (pid,))
        self.conn.commit()
