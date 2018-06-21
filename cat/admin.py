import argparse
import sqlite3
import shutil
import time
import os
import json
import math

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from cat.auth import login_required
from cat.db import get_db

BACKUP, RESET = "backup", "reset"
AVAILABLE_COMMANDS = {
    'Backup': BACKUP,
    'Reset': RESET
}

def makeURL(username):
    url = username.replace(' ', '-').lower()
    return url

bp = Blueprint('admin', __name__)

@bp.route('/admin', methods=('GET', 'POST'))
# Return the index page for the admin panel.
# This is mostly just a landing page to send us to the real controls.
def index():
    return render_template('admin/index.html', commands=AVAILABLE_COMMANDS)

@bp.route('/admin/stats', methods=('GET', 'POST'))
def stats():
    db = get_db()
    cb = db.execute(
    'select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ' where action_list.type="Community Building"'
    ).fetchone()[0]
    pc = db.execute(
    'select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ' where action_list.type="Policy Change"'
    ).fetchone()[0]
    te = db.execute(
    'select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ' where action_list.type="Training and Education"'
    ).fetchone()[0]
    total = db.execute(
    ' select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ).fetchone()[0]
    hqcb = db.execute('select count(*) from user where cb > 75').fetchone()[0]
    hqpc = db.execute('select count(*) from user where pc > 75').fetchone()[0]
    hqte = db.execute('select count(*) from user where te > 50').fetchone()[0]
    rockstars = db.execute('select count(*) from user where((cb + pc + te) >= 200 ) or (cb >= 75 and pc >= 75) or (cb >= 75 and te >= 50) or (pc >= 75 and te >= 50)').fetchone()[0]
    total_chapters = db.execute('select count(*) from user').fetchone()[0]
    hqpercent = math.floor((rockstars / total_chapters ) * 100)
    spending = db.execute('select sum(points) from spending').fetchone()[0]
    activities = db.execute('SELECT title FROM action_list')
    raw_activity_count = db.execute('select title, count(*) from action group by title')
    activity_count = {}
    for row in raw_activity_count.fetchall():
        activity_count[row[0]] = row[1]
    points = {'cb': cb, 'pc': pc, 'te': te, 'total': total, 'spending':spending}
    hq = {'cb': hqcb, 'pc': hqpc, 'te': hqte, 'hq':rockstars, 'percent':hqpercent}
    return render_template('admin/stats.html', points=points, hq=hq, activities=activities, activity_count=activity_count)

@bp.route('/admin/users', methods=('GET', 'POST'))
# This page allows us to add users to the database.
def users():
    # When someone POSTs to the page, grab the info from the form
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        permissions = request.form['permissions']
        url = makeURL(username)
        db = get_db()
        # Add to the database, with a hashed password and values at 0
        db.execute(
        'INSERT INTO user (username, password, email, permissions, cb, pc, te, balance, url)'
        ' Values (?, ?, ?, ?, 0, 0, 0, 0, ?)',
        (username, generate_password_hash(password), email, permissions, url)
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
    # Auto populate the list of Movemben Building activities from database
    mb_activities = db.execute('SELECT title FROM action_list WHERE type LIKE "Community Building"')
    # Auto populate the list of Movemben Building activities from database
    pc_activities = db.execute('SELECT title FROM action_list WHERE type LIKE "Policy Change"')
    # Auto populate the list of Movemben Building activities from database
    te_activities = db.execute('SELECT title FROM action_list WHERE type LIKE "Training and Education"')
    # Auto populate the list of chapters from the database
    chapters = db.execute(
    'SELECT username FROM user WHERE permissions LIKE "Chapter"'
    )
    chapter_list = []
    for x in chapters.fetchall():
        chapter_list.append((str(x['Username'])))

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
            'UPDATE user SET cb = cb + ? Where username = ?',
            (int(points), logged_chapter)
            )
            db.commit()

        elif type == "Training and Education":
            db.execute(
            'UPDATE user SET te = cb + ? Where username = ?',
            (int(points), logged_chapter)
            )
            db.commit()
        db.commit()
    return render_template('admin/activities.html', mb_activities=mb_activities, pc_activities=pc_activities, te_activities=te_activities, chapters=chapters, chapter_list=chapter_list)

@bp.route('/admin/spending', methods=('GET', 'POST'))
def spending():
    db = get_db()
    chapters = db.execute(
    'SELECT username FROM user WHERE permissions LIKE "Chapter"'
    )
    items = db.execute(
    'SELECT title FROM spending_list'
    )
    if request.method == 'POST':
        item = request.form['item']
        cost = request.form['cost']
        chapter = request.form['chapter']
        db = get_db()

        chapter_id = db.execute(
        'SELECT id FROM user WHERE username LIKE ?',
        (chapter,)
        ).fetchone()['id']

        db.execute(
        'UPDATE user SET balance = balance - ? Where username = ?',
        (int(cost), chapter,)
        )

        db.execute(
        'INSERT INTO spending (title, points, author_id)'
        ' Values (?, ?, ?)',
        (item, int(cost), int(chapter_id),)
        )

        db.commit()
    return render_template('admin/spending.html', chapters=chapters, items=items)

@bp.route('/admin/<cmd>')
def command(cmd=None):
    db = get_db()
    if cmd == RESET:
       db.execute('UPDATE user SET cb = 0')
       db.execute('UPDATE user SET pc = 0')
       db.execute('UPDATE user SET te = 0')

       db.commit()
       response = "Reset point counts"
    else:
        #Important to note, you must create a "backup" folder in the root directory
        backupdir = os.getcwd() + '/backups'
        dbfile = os.getcwd() + '/instance/flaskr.sqlite'
        # Create a timestamped database copy
        if not os.path.isdir(backupdir):
            raise Exception("Backup directory does not exist: {}".format(backupdir))

        backup_file = os.path.join(backupdir, os.path.basename(dbfile) +
                                   time.strftime("-%Y%m%d-%H%M%S") + '.sqlite')

        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()

        # Lock database before making a backup
        cursor.execute('begin immediate')
        # Make new backup file
        shutil.copyfile(dbfile, backup_file)
        print ("\nCreating {}...".format(backup_file))
        # Unlock database
        connection.rollback()
        response = "Backed up database"
    return response, 200, {'Content-Type': 'text/plain'}

@bp.route('/admin/user-list', methods=('GET', 'POST'))
# List all users and edit links
def userList():
    db = get_db()
    chapter_list = db.execute(
        "SELECT username, cb, pc, te, balance, permissions, url"
        " FROM user"
        " ORDER BY username ASC"
    ).fetchall()
    print(chapter_list)
    return render_template('admin/user-list.html', chapter_list=chapter_list)

@bp.route('/admin/user-edit/<url>', methods=('GET', 'POST'))
# List all users and edit links
def userEdit(url):
    db = get_db()
    user = db.execute(
        "SELECT username, email, password, permissions"
        " FROM user where url = ?", (url, )
    ).fetchone()
    if request.method =='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        permissions = request.form['permissions']
        print(user['username'])
        db.execute(
            'UPDATE user SET username = ?, email = ?, password = ?, permissions = ?'
            ' WHERE username = ?',
            (username, email, password, permissions, user['username'])
        )
        db.commit()
        return redirect(url_for('chapters.chapter', url=url))

    return render_template('admin/user-edit.html', user=user)
