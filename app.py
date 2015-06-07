#! /usr/bin/env python3

from functools import wraps
import os
import stat
import json
import datetime
import random

from flask import Flask, render_template, flash, session, request, redirect, url_for, jsonify
import misaka

import database

app = Flask(__name__)

if not os.path.isfile('/data/key'):
    with open('/data/key', 'wb') as f:
        f.write(os.urandom(32))
    os.chmod('/data/key', stat.S_IREAD)

with open('/data/key', 'rb') as f:
    app.config['SECRET_KEY'] = f.read()

app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

db = database.Database('/data/reviews.db')

def render_markdown(review):
    if review['approved'] == 1:
        review['text'] = misaka.html(review.get('text'))
    else:
        review['text'] = '<pre><code>{}</code></pre>'.format(review.get('text'))
    return review

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin' in session:
            return f(*args, **kwargs)
        else:
            flash('You are not logged in.')
            return redirect(url_for('login'))
    return wrapper

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if not db.is_new():
        flash('Database is already set up.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        appuser = db.new_appuser(request.form.to_dict())
        flash('User {} added.'.format(appuser))
        return redirect(url_for('login'))
    else:
        return render_template('admin_setup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if db.check_password(request.form.get('username'), request.form.get('password')):
            session['admin'] = request.form.get('username')
            flash('Logged in as {}.'.format(request.form.get('username')))
            return redirect(url_for('admin_reviews'))
        else:
            flash('Username or password invalid.')
            return render_template('admin_login.html')
    else:
        return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('You are logged out.')
    return redirect(url_for('login'))

@app.route('/new-user', methods=['GET', 'POST'])
@login_required
def new_user():
    if request.method == 'POST':
        form = request.form.to_dict()
        appuser = db.new_appuser(form)
        flash('User {} added.'.format(appuser))
        return redirect(url_for('admin_reviews'))
    else:
        return render_template('admin_new_user.html')

@app.route('/import', methods=['GET', 'POST'])
@login_required
def review_import():
    if request.method == 'POST':
        reviews = json.loads(request.form.get('json_data')).get('reviews')
        num_imported = db.import_reviews(reviews)
        flash('{} reviews imported.'.format(num_imported))
        return redirect(url_for('admin_reviews'))
    else:
        return render_template('admin_import.html')

@app.route('/export')
@login_required
def review_export():
    reviews = db.all_reviews()
    reviews_out = []
    for review in reviews:
        reviews_out.append({k: dict(review).get(k, None) for k in ('id', 'title', 'text', 'author', 'created', 'approved')})
    return jsonify(reviews=reviews_out)

@app.route('/toggle-approved/<id>')
@login_required
def toggle_approved(id):
    db.toggle_approved(id)
    return redirect(url_for('admin_reviews'))

@app.route('/delete', methods=['POST'])
@app.route('/delete/<id>')
@login_required
def delete_review(id=None):
    if request.method == 'POST':
        review = db.delete_review(request.form.get('id'))
        flash('Review has been deleted.')
        return redirect(url_for('admin_reviews'))
    else:
        review = render_markdown(db.get_review(id))
        return render_template('admin_delete.html', review=review)

@app.route('/edit', methods=['POST'])
@app.route('/edit/<id>')
@login_required
def edit_review(id=None):
    if request.method == 'POST':
        review = request.form.to_dict()
        db.edit_review(review)
        flash('Review updated.')
        return redirect(url_for('admin_reviews'))
    else:
        review = db.get_review(id)
        return render_template('admin_edit.html', review=review)

@app.route('/')
@login_required
def admin_reviews():
    reviews = db.all_reviews()
    for review in reviews:
        review = render_markdown(review)
        review['created'] = datetime.datetime.fromtimestamp(review['created']).strftime('%A %B %d %Y %H:%M:%S')
    return render_template('admin_reviews.html', reviews=reviews)

@app.route('/submit-review', methods=['POST'])
def submit_review():
    review = {k: request.form.get(k) for k in ('title', 'text', 'author')}
    db.submit(review)
    return redirect('http://ctrends.net/review-thank-you')

@app.route('/reviews.json')
def get_reviews():
    reviews = db.approved_reviews()
    reviews_out = []
    for review in reviews:
        review = render_markdown(review)
        reviews_out.append({k: dict(review).get(k, None) for k in ('title', 'text', 'author')})
    return jsonify(reviews=reviews_out), 200, {'Access-Control-Allow-Origin': '*'}

@app.route('/random-review.json')
def get_random_review():
    review = random.choice(db.approved_reviews())
    review = render_markdown(review)
    review = {k: dict(review).get(k) for k in ('title', 'text', 'author')}
    return jsonify(review=review), 200, {'Access-Control-Allow-Origin': '*'}

if __name__ == '__main__':
    app.run(host='0.0.0.0')
