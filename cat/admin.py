from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from cat.auth import login_required
from cat.db import get_db

admin = 'admin'

bp = Blueprint('admin', __name__)

@bp.route('/admin', methods=('GET', 'POST'))
def index():
    return render_template('admin/index.html')

@bp.route('/admin/users', methods=('GET', 'POST'))
def users():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        permissions = request.form['permissions']
        db = get_db()
        db.execute(
            'INSERT INTO user (username, password, permissions, cb, pc, te, balance)'
            ' Values (?, ?, ?, 0, 0, 0, 0)',
            (username, generate_password_hash(password), permissions)
        )
        db.commit()
    return render_template('admin/users.html')

@bp.route('/admin/categories', methods=('GET', 'POST'))
def categories():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        type = request.form['type']
        db = get_db()
        db.execute(
            'INSERT INTO action_list (title, description, type)'
            ' Values (?, ?, ?)',
            (title, description, type)
        )
        db.commit()
    return render_template('admin/categories.html')

@bp.route('/admin/activities', methods=('GET', 'POST'))
def activities():
    if request.method == 'POST':
        activity = request.form['name']
        points = request.form['points']
        logged_chapter = request.form['chapter']
        db = get_db()
        db.execute(
            'INSERT INTO action (title, points, author_id)'
            ' Values (?, ?, ?)',
            (activity, points, logged_chapter)
        )
        # Update Chapter Building, Policy Change, or Training and Education Points on the Chapter profiles.
        # if title == 'policy':
        #     db.execute(
        #         'UPDATE user SET pc = pc + ? Where id = ?',
        #         (int(points), g.user['id'])
        #     )
        # elif title == 'community':
        #     db.execute(
        #         'UPDATE user SET cb = ? Where id = ?',
        #         (int(points), g.user['id'])
        #     )
        # elif title == 'education':
        #     db.execute(
        #         'UPDATE user SET te = ? Where id = ?',
        #         (int(points), g.user['id'])
        #     )
        db.commit()
    return render_template('admin/activities.html')

@bp.route('/admin/spending', methods=('GET', 'POST'))
def spending():
    if request.method == 'POST':
        item = request.form['item']
        cost = request.form['cost']
        chapter = request.form['chapter']
        db = get_db()
        db.execute(
            'INSERT INTO spending (title, points, author_id)'
            ' Values (?, ?, ?)',
            (item, cost, chapter)
        )
        db.commit()
    return render_template('admin/spending.html')
