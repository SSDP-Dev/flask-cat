from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from cat.auth import login_required
from cat.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    actions = db.execute(
    'SELECT title, author_id, points, note'
    ' FROM action'
    ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', actions=actions)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['activity']
        points = request.form['points']
        note = request.form['note']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO action (title, points, note, author_id)'
                ' Values (?, ?, ?, ?)',
                (title, points, note, g.user['id'])
            )
            # Update Chapter Building, Policy Change, or Training and Education Points on the Chapter profiles.
            if title == 'policy':
                db.execute(
                    'UPDATE user SET pc = pc + ? Where id = ?',
                    (int(points), g.user['id'])
                )
            elif title == 'community':
                db.execute(
                    'UPDATE user SET cb = ? Where id = ?',
                    (int(points), g.user['id'])
                )
            elif title == 'education':
                db.execute(
                    'UPDATE user SET te = ? Where id = ?',
                    (int(points), g.user['id'])
                )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method =='POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/leaderboard')
def leaderboard():
    db = get_db()
    chapters = db.execute(
        "SELECT username, cb, pc, te, balance, permissions"
        " FROM user WHERE permissions LIKE 'Chapter'"
        " ORDER BY balance DESC"
    ).fetchall()
    return render_template('blog/leaderboard.html', chapters=chapters)

@bp.route('/available-activities')
def availableActivities():
    db = get_db()
    activities = db.execute(
    'SELECT title, description, type'
    ' FROM action_list'
    ).fetchall()
    return render_template('blog/available-activities.html', activities=activities)

@bp.route('/faq')
def faq():
    return render_template('blog/faq.html')

@bp.route('/store')
def store():
    return render_template('blog/store.html')
