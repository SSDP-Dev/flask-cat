#This is where all the administrative functions and pages live.
#The index, at /admin, is a landing page for all those pages and functions.
#It should just be a column of buttons that include links and fuctions for users to control their CAT experience.
# Users with the permissions 'Admin' can see all of the controls. 'Staffer' gets fewer. 'Chapter' gets the least.

#Import utility things like sql, time, os, json, math, etc.
import argparse
import sqlite3
import shutil
import time
import os
import json
import math
#Import flask modules needed for the framework.
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
#Import security functions for password hashes.
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
#Import the login_required function and a way to get the database.
from cat.auth import login_required
from cat.db import get_db
#These constants set up two of the 'command' buttons.
#I wanted to have a few buttons that just did something without a page
#So I followed a tutorial and these are from that
#I'm pretty sure all this does is create a const dictionary of terms
#To dictate what buttons and commands we have.
BACKUP, RESET = "backup", "reset"
AVAILABLE_COMMANDS = {
    'Backup': BACKUP,
    'Reset': RESET
}

#We use makeURL when creating a new chapter
#This function take the entered username and generates a url in our format
def makeURL(username):
    url = username.replace(' ', '-').lower()
    return url

#Flask framework requirement, sets up a blueprint. Not sure how this all works
#Looks like Blueprint is some sort of class and it has the .route() method
bp = Blueprint('admin', __name__)

#Root page for the admin pages. /admin
@bp.route('/admin', methods=('GET', 'POST'))
# Return the index page for the admin panel.
# This is mostly just a landing page to send us to the real controls.
def index():
    return render_template('admin/index.html', commands=AVAILABLE_COMMANDS)

# This returns a stats page for staff users.
# You can't actually get here from the index, it's listed in the header
# Right now it's public, but we could hide it in the future behind permissions
@bp.route('/admin/stats', methods=('GET', 'POST'))
def stats():
    db = get_db()
    # Sums up how many community building points are in the database.
    cb = db.execute(
    'select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ' where action_list.type="Community Building"'
    ).fetchone()[0]
    # Sums up how many policy change points are in the database.
    pc = db.execute(
    'select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ' where action_list.type="Policy Change"'
    ).fetchone()[0]
    # Sums up how many training and education points are in the database.
    te = db.execute(
    'select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ' where action_list.type="Training and Education"'
    ).fetchone()[0]
    # Sums up total points in the database
    total = db.execute(
    ' select sum(action.points)'
    ' FROM action'
    ' INNER JOIN action_list ON action.title=action_list.title'
    ).fetchone()[0]
    # Counts how many chapters have over 75 community building points
    hqcb = db.execute('select count(*) from user where cb > 75').fetchone()[0]
    # Counts how many chapters have over 75 policy change points
    hqpc = db.execute('select count(*) from user where pc > 75').fetchone()[0]
    # Counts how many chapters have over 50 training and education points
    hqte = db.execute('select count(*) from user where te > 50').fetchone()[0]
    # A rockstar, or high quality chapter has the following criteria
    # Either 200+ total points (cb + pc + te)
    # Or they've filled up 2 out of 3 of the buckets
    # The rockstars query searches for those criteria in the line below
    # We can change it if we change the high quality criteria, which happens
    rockstars = db.execute('select count(*) from user where((cb + pc + te) >= 200 ) or (cb >= 75 and pc >= 75) or (cb >= 75 and te >= 50) or (pc >= 75 and te >= 50)').fetchone()[0]
    # We want to know how many total chapters there are.
    # We may supplement this with an "active" flag or something to denote DEF
    total_chapters = db.execute('select count(*) from user').fetchone()[0]
    # Calculates the percentage of high quality chapters total
    hqpercent = math.floor((rockstars / total_chapters ) * 100)
    # How many points have been spent
    spending = db.execute('select sum(points) from spending').fetchone()[0]
    # In the page template, we'll be listing out all the available activities
    # So this query gives us that list
    activities = db.execute('SELECT title FROM action_list')
    # This gives us the count of how many of each activity have been done
    raw_activity_count = db.execute('select title, count(*) from action group by title')
    # Initialize an empty dictionary
    activity_count = {}
    # Create a dictionary with the key/value pair of "Activity" : Count
    for row in raw_activity_count.fetchall():
        activity_count[row[0]] = row[1]
    # Create a dictionary with the overall points stats
    points = {'cb': cb, 'pc': pc, 'te': te, 'total': total, 'spending':spending}
    # Create a dictionary with the high quality stats
    hq = {'cb': hqcb, 'pc': hqpc, 'te': hqte, 'hq':rockstars, 'percent':hqpercent}
    # Render page, pass in the dictionaries for processing
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
        # makeURL is defined at the top of this file right now
        # It takes a username and gives us a nicer slug format for the url
        url = makeURL(username)
        db = get_db()
        # Add to the database, with a hashed password and values at 0
        db.execute(
        'INSERT INTO user (username, password, email, permissions, cb, pc, te, balance, url)'
        ' Values (?, ?, ?, ?, 0, 0, 0, 0, ?)',
        (username, generate_password_hash(password), email, permissions, url)
        )
        db.commit()
        # Redirect to the new chapter page
        return redirect(url_for('chapters.chapter', url=url))
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
        # Redirect to the available Activities page
        return redirect(url_for('blog.availableActivities'))
    return render_template('admin/categories.html')

@bp.route('/admin/activities', methods=('GET', 'POST'))
# This page allows us to log activities to the database.
def activities():
    db = get_db()
    # Retrieve the list of Movement Building activities from database
    mb_activities = db.execute('SELECT title FROM action_list WHERE type LIKE "Community Building"')
    # Retrieve the list of Policy Change activities from database
    pc_activities = db.execute('SELECT title FROM action_list WHERE type LIKE "Policy Change"')
    # Retrive the list of Training and Education activities from database
    te_activities = db.execute('SELECT title FROM action_list WHERE type LIKE "Training and Education"')
    # Retrieve the list of chapters from the database
    chapters = db.execute('SELECT username FROM user WHERE permissions LIKE "Chapter"')
    # Init an empty list for the chapter listing
    chapter_list = []
    # Push the usernames into the chapter list for ease of use in search bar on page
    for x in chapters.fetchall():
        chapter_list.append((str(x['Username'])))

    if request.method == 'POST':
        # If we post to the page, add the activity to the action table
        activity = request.form['activity']
        points = request.form['points']
        # If the user is an Administrator or Staffer, they can use the select chapter form, so we pull from it 
        if g.user['permissions'] == 'Admin' or g.user['permissions'] == 'Staffer':
            logged_chapter = request.form['chapter']
        # If the user is a chapter, they can only log points for themselves, so we default to their username
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
        #Check if password was left blank. If it's blank, just use the same password. If not, hash it and insert.
        if request.form['password'] != "":
            password = generate_password_hash(request.form['password'])
        else:
            password = user['password']
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
