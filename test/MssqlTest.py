import unittest

from core.Mssql import Mssql, MssqlTarget
from pyodbc import InterfaceError


class TestMssql(unittest.TestCase):
    username = 'sa'
    password = '132132qq'
    false_pw = '132132'
    dsn = 'a'

    def test_connect_db(self):
        mssql = Mssql(self.username,
                      self.false_pw,
                      self.dsn,
                      None)
        result = mssql.connect_db()
        self.assertEqual(result[0], False)
        self.assertIsNone(mssql.engine)
        self.assertIsNone(mssql.conn)
        mssql.password = self.password
        mssql.connect_db()
        self.assertIsNotNone(mssql.engine)
        self.assertIsNotNone(mssql.conn)

    def test_is_connected(self):
        mssql = Mssql(self.username,
                      self.password,
                      self.dsn,
                      None)
        self.assertFalse(mssql.is_connected())
        mssql.connect_db()
        self.assertTrue(mssql.is_connected())
        mssql2 = Mssql(self.username,
                       self.false_pw,
                       self.dsn,
                       None)
        mssql.connect_db()
        self.assertFalse(mssql2.is_connected())

    def test_set_table(self):
        mssql = Mssql(self.username,
                      self.password,
                      self.dsn,
                      None)
        mssql.connect_db()
        table_name = mssql.list_table()[0]
        self.assertFalse(mssql.set_table('qljf56qea'))
        self.assertIsNone(mssql.table)
        self.assertTrue(mssql.set_table(table_name))
        self.assertIsNotNone(mssql.table)
        self.assertEqual(table_name, mssql.table.name)


class TestMssqlTarget(unittest.TestCase):

    def test_create_table(self):

        pass


class TestMssqlSource(unittest.TestCase):
    pass

