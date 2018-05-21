from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from cat.auth import login_required
from cat.db import get_db

bp = Blueprint('admin', __name__)

@bp.route('/admin', methods=('GET', 'POST'))
# Return the index page for the admin panel.
# This is mostly just a landing page to send us to the real controls.
def index():
    return render_template('admin/index.html')

@bp.route('/admin/users', methods=('GET', 'POST'))
# This page allows us to add users to the database.
def users():
    # When someone POSTs to the page, grab the info from the form
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        permissions = request.form['permissions']
        db = get_db()
        # Add to the database, with a hashed password and values at 0
        db.execute(
        'INSERT INTO user (username, password, email, permissions, cb, pc, te, balance)'
        ' Values (?, ?, ?, ?, 0, 0, 0, 0)',
        (username, generate_password_hash(password), email, permissions)
        )
        db.commit()
    return render_template('admin/users.html')

@bp.route('/admin/categories', methods=('GET', 'POST'))
# This page allows us to add categories to the database.
def categories():
    if request.method == 'POST':
        # When someone POSTs to the page, grab the info from the form
        title = request.form['title']
        description = request.form['description']
        type = request.form['type']
        db = get_db()
        # Add to the database
        db.execute(
        'INSERT INTO action_list (title, description, type)'
        ' Values (?, ?, ?)',
        (title, description, type)
        )
        db.commit()
    return render_template('admin/categories.html')

@bp.route('/admin/activities', methods=('GET', 'POST'))
# This page allows us to log activities to the database.
def activities():
    db = get_db()
    # Auto populate the list of activities from database
    activities = db.execute('SELECT title FROM action_list')
    # Auto populate the list of chapters from the database
    chapters = db.execute(
    'SELECT username FROM user WHERE permissions LIKE "Chapter"'
    )
    if request.method == 'POST':
        # If we post to the page, add the activity to the action table
        activity = request.form['activity']
        points = request.form['points']
        # If the user is an Administrator or Staffer, they can use the select
        if g.user['permissions'] == 'Admin' or g.user['permissions'] == 'Staffer':
            logged_chapter = request.form['chapter']
        # If the user is a chapter, they can only log points for themselves
        else:
            logged_chapter = g.user['username']
        # This returns the type of activity, by searching by title
        type = db.execute(
        'SELECT type FROM action_list WHERE title LIKE ?', (activity,)
        ).fetchone()[0]
        db.execute(
        'INSERT INTO action (title, points, author_id)'
        ' Values (?, ?, ?)',
        (activity, points, logged_chapter)
        )
        # We also add to the balance of the logged chapter
        db.execute(
        'UPDATE user SET balance = balance + ? Where username = ?',
        (int(points), logged_chapter)
        )
        # Update Chapter Building, Policy Change, or Training and Education
        # This is based on type, which we get above.
        if type == "Policy Change":
            db.execute(
            'UPDATE user SET pc = pc + ? Where username = ?',
            (int(points), logged_chapter)
            )
            db.commit()
        elif type == "Community Building":
            db.execute(
            'UPDATE user SET cb = ? Where username = ?',
            (int(points), logged_chapter)
            )
            db.commit()

        elif type == "Training and Education":
            db.execute(
            'UPDATE user SET te = ? Where username = ?',
            (int(points), logged_chapter)
            )
            db.commit()
        db.commit()
    return render_template('admin/activities.html', activities=activities, chapters=chapters)

@bp.route('/admin/spending', methods=('GET', 'POST'))
def spending():
    db = get_db()
    chapters = db.execute(
    'SELECT username FROM user WHERE permissions LIKE "Chapter"'
    )
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
    return render_template('admin/spending.html', chapters=chapters)
