#! /usr/bin/env python3

import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        conn = self.db_conn()
        conn.execute('create table if not exists reviews (id text primary key not null, title, text, author, created)')
        conn.execute('create table if not exists appusers (appuser text primary key not null, password)')

    def db_conn(self):
        conn = sqlite3.connect(self.dbfile)
        conn.row_factory = sqlite3.Row
        return conn

    def is_new(self):
        conn = self.db_conn()
        return len(conn.execute('select appuser from appusers').fetchall()) == 0
