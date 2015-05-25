#! /usr/bin/env python3

import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        conn = self.db_conn()
        conn.execute('create table if not exists reviews (id text primary key not null, title, text, author, created)')
        conn.execute('create table if not exists appusers (appuser text primary key not null, password)')
        conn.commit()
        conn.close()

    def db_conn(self):
        conn = sqlite3.connect(self.dbfile)
        conn.row_factory = sqlite3.Row
        return conn

    def is_new(self):
        conn = self.db_conn()
        num_appusers = len(conn.execute('select appuser from appusers').fetchall())
        conn.close()
        return num_appusers == 0

    def new_appuser(self, form):
        conn = self.db_conn()
        cur = conn.cursor()
        password_hash = generate_password_hash(form.get('password'), method='pbkdf2:sha256')
        cur.execute('insert into appusers values (?, ?)', (form.get('appuser'), password_hash))
        rowid = cur.lastrowid
        appuser = conn.execute('select appuser from appusers where rowid=?', (rowid,)).fetchone()[0]
        conn.commit()
        conn.close()
        return appuser

    def check_password(self, appuser, password):
        conn = self.db_conn()
        password_hash = conn.execute('select password from appusers where appuser=?', (appuser,)).fetchone()[0]
        conn.close()
        return check_password_hash(password_hash, password)
