# This class came from the [Flaskr tutorial](http://flask.pocoo.org/docs/1.0/tutorial/) as well.
# The tutorial gave me a few things like creating 'blog posts' and editing them, so I kept the bulk of that to use with actions.
# I never changed it from `blog` because I didn't want to create any weird bugs.

# Flask imports
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
# Import abort from werkzeug
from werkzeug.exceptions import abort

# Get the login_required and get_db methods from other CAT classes
from cat.auth import login_required
from cat.db import get_db

bp = Blueprint('blog', __name__)

# The home page for /
@bp.route('/')
def index():
    db = get_db()
    # Retrieve all the actions in the database
    # Eventually, we'll only want to display them for this year (maybe)
    actions = db.execute(
    'SELECT title, author_id, points, note, id'
    ' FROM action'
    ' ORDER BY created DESC'
    ).fetchall()
    # Retreive list of all users
    chapters = db.execute(
    'SELECT * from user'
    ).fetchall()
    return render_template('blog/index.html', actions=actions, chapters=chapters)

# This page allows us to create actions
@bp.route('/create', methods=('GET', 'POST'))
# A person must be logged in to do this. Not a bad idea to add this to more methods
# But that's a later thing.
# OK, after starting to document this, I found that we're not actually using this for action creation
# Which is good, because it clearly doesn't do it correctly
# Action creation is happening through admin.activities()
# Eventually, we'll want to remove this - for now I won't touch anything to avoid bugs
# 6/21/18
@login_required
def create():
    # If we POST to the page, grabe the activity, points, and note.
    if request.method == 'POST':
        title = request.form['activity']
        points = request.form['points']
        note = request.form['note']
        # This error handling stuff is from the tutorial, and I didn't do a great job implementing it elswhere
        # I haven't taken the time to fully understand what's going on here, but I will eventually.
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # Insert the action info into the database
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
    # Returns an action based on the id
    post = get_db().execute(
        'SELECT * from action WHERE id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post

# We are definitely, definitely using this update function to change action details, though
# That's for sure
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # get the action, from get_action
    post = get_action(id)
    # old point value of the action
    old_points = post['points']
    # Author of the action
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
            # Update the action
            db.execute(
                'UPDATE action SET points = ?, note = ?'
                ' WHERE id = ?',
                (points, note, id)
            )
            # Set the balance to the delta of the new value
            db.execute('UPDATE user SET balance = balance + ? WHERE username = ?', (points_delta, author,))
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

# This function allows us to delete actions
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # Get the action with the id supplied
    target_action = get_action(id)
    db = get_db()
    # Find the author of this specific activity
    author = db.execute('SELECT author_id from action WHERE id = ?', (id,)).fetchone()['author_id']
    # Get the point value of the action, to be subtracted later
    action_value = db.execute('SELECT points from action where id = ?', (id,)).fetchone()['points']
    # Get the type of the action so we can subtract points from the correct place
    type = db.execute('SELECT * from action_list WHERE title = ?', (target_action['title'], )).fetchone()['type']
    # Delete it
    db.execute('DELETE FROM action WHERE id = ?', (id,))
    # Change the balance for the author
    db.execute('UPDATE user SET balance = balance - ? where username = ?', (action_value, author,))
    #If type = policy change, update that field for the user
    if type == "Policy Change":
        #Update the policy change poins with differential.
        db.execute(
            'UPDATE user SET pc = pc - ? WHERE username = ?', (action_value, author,)
        )
        db.commit()
    #If type = community building, update that field for the user
    elif type == "Community Building":
        #Update the community building points with differential
        db.execute(
            'UPDATE user SET cb = cb - ? WHERE username = ?', (action_value, author,)
        )
        db.commit()
    #If type = training and education, update that field for the user
    elif type == "Training and Education":
        #Update the T&E points with differential
        db.execute(
            'UPDATE user SET te = te - ? WHERE username = ?', (action_value, author,)
        )
        db.commit()
    db.commit()
    # Return to home page
    return redirect(url_for('blog.index'))

# This function spits out the leaderboard
@bp.route('/leaderboard')
def leaderboard():
    db = get_db()
    # Get chapter data for users with Chapter permissions, order by the sum of cb + pc + te
    # Ordering by balance won't work well, since balance is more for spending and won't be clean
    chapters = db.execute(
        "SELECT username, cb, pc, te, balance, permissions, url"
        " FROM user WHERE permissions LIKE 'Chapter'"
        " ORDER BY cb + pc + te DESC"
    ).fetchall()
    return render_template('blog/leaderboard.html', chapters=chapters)

# This function gives us the available activities page
@bp.route('/available-activities')
def availableActivities():
    db = get_db()
    # Retrive the activities list
    activities = db.execute(
    'SELECT title, description, type'
    ' FROM action_list'
    ).fetchall()
    return render_template('blog/available-activities.html', activities=activities)

# This function gives us the FAQ page
@bp.route('/faq')
def faq():
    return render_template('blog/faq.html')

# This function gives us the store page, but may be DEF if we use the create spending the admin class
@bp.route('/store')
def store():
    return render_template('blog/store.html')
