import pytest
from mock import (
    patch,
    Mock,
)
from tests.base import BaseTest
from tests.mocks import MockTunnel
from tunnel.db import Database


class TestDatabase(BaseTest):
    @patch('tunnel.db.sqlite3')
    @patch('tunnel.db.os')
    def test_init(self, mock_os, mock_sql):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sql.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_os.path.exists.return_value = False
        mock_os.path.expanduser('/home/ubuntu')
        Database()
        assert mock_os.mkdir.called_once_with('/home/ubuntu/.tunnelfox')
        assert mock_sql.connect.called_once_with(
            '/home/ubuntu/.tunnelfox/tunnelfox.db')
        assert mock_cursor.execute.called_once_with(
            "CREATE TABLE IF NOT EXISTS tunnel (server text, "
            "remote integer, local integer, name text, pid integer)")
        assert mock_conn.commit.called_once()

    @patch('tunnel.db.sqlite3')
    @patch('tunnel.db.os')
    def test_close(self, mock_os, mock_sql):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sql.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_os.path.exists.return_value = False
        mock_os.path.expanduser('/home/ubuntu')
        d = Database()
        d.close()
        mock_conn.close.assert_called()

    @patch('tunnel.db.sqlite3')
    @patch('tunnel.db.os')
    def test_create_tunnel(self, mock_os, mock_sql):
        t = MockTunnel('host', 8080)
        t.start()
        t.pid = 5
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sql.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_os.path.exists.return_value = False
        mock_os.path.expanduser('/home/ubuntu')
        d = Database()
        d.create_tunnel(t)
        sql = "INSERT INTO tunnel VALUES('host', 8080, 8080, 'localhost', 5)"
        mock_cursor.execute.assert_called_with(sql)

    @patch('tunnel.db.sqlite3')
    @patch('tunnel.db.os')
    def test_create_tunnel_no_pid(self, mock_os, mock_sql):
        t = MockTunnel('host', 8080)
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sql.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_os.path.exists.return_value = False
        mock_os.path.expanduser('/home/ubuntu')
        d = Database()
        with pytest.raises(Exception):
            d.create_tunnel(t)

    @patch('tunnel.db.sqlite3')
    @patch('tunnel.db.os')
    def test_in_use(self, mock_os, mock_sql):
        t = MockTunnel('host', 8080)
        t.start()
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sql.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = t
        mock_os.path.exists.return_value = False
        mock_os.path.expanduser('/home/ubuntu')
        d = Database()
        d.create_tunnel(t)
        params = (t.server, t.remote, t.local, t.name)
        in_use = d.in_use(*params)
        sql = ("SELECT * FROM tunnel WHERE server=? AND "
               "remote=? AND local=? AND name=?")
        mock_cursor.execute.assert_called_with(sql, params)
        mock_cursor.fetchone.assert_called_once()
        assert in_use

    @patch('tunnel.db.sqlite3')
    @patch('tunnel.db.os')
    def test_not_in_use(self, mock_os, mock_sql):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_sql.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_os.path.exists.return_value = False
        mock_os.path.expanduser('/home/ubuntu')
        d = Database()
        in_use = d.in_use('host', 8080, 8080)
        assert not in_use
