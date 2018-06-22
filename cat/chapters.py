# This class provides methods to work with chapter data. It's a bit more front facing.

# Flask imports
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

# Import from cat.auth and cat.db - login required and get_db
from cat.auth import login_required
from cat.db import get_db

# We need math for some stats rendering in chapter()
import math

bp = Blueprint('chapters', __name__)

# The index page just displays a list of all chapters
@bp.route('/chapters')
def index():
    db = get_db()
    # Retrieve all the chapters, some of their data, and order by username alphabetically
    chapters = db.execute(
        'SELECT username, cb, pc, te, permissions, url'
        ' FROM user'
        ' ORDER BY username ASC'
    ).fetchall()
    return render_template('chapters/index.html', chapters=chapters)

def get_chapter(url):
    # Return a specific chapter
    chapter = get_db().execute(
    'SELECT username, cb, pc, te, balance, url'
    ' FROM user WHERE url = ?',
    (url,)
    ).fetchone()

    if chapter is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return chapter

# This is a specific chapter page, gives us chapter stats and an activity feed for that chapter itself
@bp.route('/<url>/', methods=('GET', 'POST'))
def chapter(url):
    db = get_db()
    # Whoops, target_user is basically the return of get_chapter. We can clean that up later
    target_user = db.execute('SELECT username from user where url = ?',
    (url,)).fetchone()
    # Retrieve all the actions authored by this chapter
    actions = db.execute(
    'SELECT * from action where author_id = ?', (target_user)
    ).fetchall()
    # Retrieve the chapter with get_chapter
    chapter = get_chapter(url)
    # Rave values for community building, policy change, and training and education
    raw_cb = chapter['cb']
    raw_pc = chapter['pc']
    raw_te = chapter['te']
    # We're going to use these percentages to fill up the progress bars with CSS
    cb_percent = math.floor((raw_cb / 75) * 100)
    pc_percent = math.floor((raw_pc / 75) * 100)
    te_percent = math.floor((raw_te / 50) * 100)
    # No need to fill a progress bar more than 100%
    if cb_percent > 100:
        cb_percent = 100

    if pc_percent > 100:
        pc_percent = 100

    if te_percent > 100:
        te_percent = 100
    # A dictionary of those percentages to pass to the page template
    points = {'cb': cb_percent, 'pc': pc_percent, 'te': te_percent}

    return render_template('chapters/chapter.html', chapter=chapter, points = points, actions=actions)
