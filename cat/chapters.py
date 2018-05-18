from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from cat.auth import login_required
from cat.db import get_db

bp = Blueprint('chapters', __name__)

@bp.route('/chapters')
def index():
    db = get_db()
    chapters = db.execute(
        'SELECT username, cb, pc, te'
        ' FROM user'
        ' ORDER BY username DESC'
    ).fetchall()
    return render_template('chapters/index.html', chapters=chapters)

def get_chapter(username):
    chapter = get_db().execute(
    'SELECT username, cb, pc, te, balance'
    ' FROM user WHERE username = ?',
    (username,)
    ).fetchone()

    if chapter is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return chapter

@bp.route('/<username>/', methods=('GET', 'POST'))
@login_required
def display(username):
    chapter = get_chapter(username)

    return render_template('chapters/chapter.html', chapter=chapter)
#
# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM post WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('blog.index'))
