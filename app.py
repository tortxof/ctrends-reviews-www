#! /usr/bin/env python3

from functools import wraps
import os

from flask import Flask, render_template, flash, session, request, redirect, url_for, jsonify

import database

app = Flask(__name__)

if not os.path.isfile('key'):
    with open('key', 'w') as f:
        print(codecs.encode(os.urandom(32), 'hex').decode(), file=f)
with open('key') as f:
    app.config['SECRET_KEY'] = f.read()

db = database.Database('reviews.db')

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin' in session:
            return f(*args, **kwargs)
        else:
            flash('You are not logged in.')
            return redirect(url_for('login'))
    return wrapper

@app.route('setup', methods=['GET', 'POST'])
def setup():
    if not db.is_new():
        flash('Database is already set up.')
        return redirect(url_for('login'))
    if request.method = 'POST':
        appuser = db.new_appuser(request.form.to_dict())
        flash('User {} added.'.format(appuser))
        return redirect(url_for('login'))
    else:
        return render_template('admin_setup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method = 'POST':
        pass
    else:
        return render_template('admin_login.html')

@app.route('/reviews.json')
def get_reviews():
    pass

if __name__ == '__main__':
    app.run()
