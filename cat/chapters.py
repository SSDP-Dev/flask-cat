from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from cat.auth import login_required
from cat.db import get_db

import math

bp = Blueprint('chapters', __name__)

@bp.route('/chapters')
def index():
    db = get_db()
    chapters = db.execute(
        'SELECT username, cb, pc, te, permissions, url'
        ' FROM user'
        ' ORDER BY username ASC'
    ).fetchall()
    return render_template('chapters/index.html', chapters=chapters)

def get_chapter(url):
    chapter = get_db().execute(
    'SELECT username, cb, pc, te, balance, url'
    ' FROM user WHERE url = ?',
    (url,)
    ).fetchone()

    if chapter is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return chapter

@bp.route('/<url>/', methods=('GET', 'POST'))
def chapter(url):
    db = get_db()
    target_user = db.execute('SELECT username from user where url = ?',
    (url,)).fetchone()
    actions = db.execute(
    'SELECT * from action where author_id = ?', (target_user)
    ).fetchall()
    chapter = get_chapter(url)
    raw_cb = chapter['cb']
    raw_pc = chapter['pc']
    raw_te = chapter['te']

    cb_percent = math.floor((raw_cb / 75) * 100)
    pc_percent = math.floor((raw_pc / 75) * 100)
    te_percent = math.floor((raw_te / 50) * 100)

    if cb_percent > 100:
        cb_percent = 100

    if pc_percent > 100:
        pc_percent = 100

    if te_percent > 100:
        te_percent = 100

    points = {'cb': cb_percent, 'pc': pc_percent, 'te': te_percent}

    return render_template('chapters/chapter.html', chapter=chapter, points = points, actions=actions)
