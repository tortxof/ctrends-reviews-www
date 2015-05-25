#! /usr/bin/env python3

import sqlite3
import os
import base64
import datetime

from werkzeug.security import generate_password_hash, check_password_hash

class Database(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        conn = self.db_conn()
        conn.execute('create table if not exists reviews (id text primary key not null, title, text, author, approved, created)')
        conn.execute('create table if not exists appusers (appuser text primary key not null, password)')
        conn.commit()
        conn.close()

    def new_id(self):
        return base64.urlsafe_b64encode(os.urandom(24)).decode()

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

    def import_reviews(self, reviews):
        conn = self.db_conn()
        for review in reviews:
            if 'id' not in review:
                review['id'] = self.new_id()
            review['created'] = datetime.datetime.utcnow().isoformat()
            review['approved'] = 1
            conn.execute('insert into reviews values (:id, :title, :text, :author, :approved, :created)', review)
        conn.commit()
        num_rows = conn.total_changes
        conn.close()
        return num_rows

    def all_reviews(self):
        conn = self.db_conn()
        reviews = conn.execute('select * from reviews').fetchall()
        conn.close()
        return reviews

    def approved_reviews(self):
        conn = self.db_conn()
        reviews = conn.execute('select * from reviews where approved=1').fetchall()
        conn.close()
        return reviews

    def get_review(self, id):
        conn = self.db_conn()
        review = conn.execute('select * from reviews where id=?', (id,)).fetchone()
        conn.close()
        return review

    def delete_review(self, id):
        conn = self.db_conn()
        review = conn.execute('select * from reviews where id=?', (id,)).fetchone()
        conn.execute('delete from reviews where id=?', (id,))
        conn.commit()
        conn.close()
        return review

    def submit(self, review):
        review['id'] = self.new_id()
        review['created'] = datetime.datetime.utcnow().isoformat()
        review['approved'] = 0
        conn = self.db_conn()
        conn.execute('insert into reviews values (:id, :title, :text, :author, :approved, :created)', review)
        conn.commit()
        conn.close()

    def toggle_approved(self, id):
        conn = self.db_conn()
        approved = conn.execute('select approved from reviews where id=?', (id,)).fetchone()[0]
        if approved != 0:
            approved = 0
        else:
            approved = 1
        conn.execute('update reviews set approved=? where id=?', (approved, id))
        conn.commit()
        conn.close()
