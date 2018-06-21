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
    'SELECT title, author_id, points, note, id'
    ' FROM action'
    ' ORDER BY created DESC'
    ).fetchall()
    chapters = db.execute(
    'SELECT * from user'
    ).fetchall()
    return render_template('blog/index.html', actions=actions, chapters=chapters)

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

def get_action(id):
    post = get_db().execute(
        'SELECT * from action WHERE id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_action(id)
    old_points = post['points']
    author = post['author_id']
    # Get title from selected action
    title = post['title']
    # Get type from action_list where title == title
    db = get_db()
    url = db.execute('SELECT * from user WHERE username = ?', (author,)).fetchone()['url']
    type = db.execute('SELECT * from action_list WHERE title = ?', (title, )).fetchone()['type']
    if request.method =='POST':
        points = request.form['points']
        note = request.form['note']
        error = None
        #Calculate the differential between the new point count and the old points
        points_delta = int(points) -  int(old_points)
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE action SET points = ?, note = ?'
                ' WHERE id = ?',
                (points, note, id)
            )
            db.commit()
            #If type = policy change, update that field for the user
            if type == "Policy Change":
                #Update the policy change poins with differential.
                db.execute(
                    'UPDATE user SET pc = pc + ? WHERE username = ?', (points_delta, author,)
                )
                db.commit()
            #If type = community building, update that field for the user
            elif type == "Community Building":
                #Update the community building points with differential
                db.execute(
                    'UPDATE user SET cb = cb + ? WHERE username = ?', (points_delta, author,)
                )
                db.commit()
            #If type = training and education, update that field for the user
            elif type == "Training and Education":
                #Update the T&E points with differential
                db.execute(
                    'UPDATE user SET te = te + ? WHERE username = ?', (points_delta, author,)
                )
                db.commit()
            return redirect(url_for('chapters.chapter', url=url))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_action(id)
    db = get_db()
    db.execute('DELETE FROM action WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/leaderboard')
def leaderboard():
    db = get_db()
    chapters = db.execute(
        "SELECT username, cb, pc, te, balance, permissions, url"
        " FROM user WHERE permissions LIKE 'Chapter'"
        " ORDER BY cb + pc + te DESC"
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
