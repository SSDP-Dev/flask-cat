from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from cat.auth import login_required
from cat.db import get_db

admin = 'admin'

bp = Blueprint('admin', __name__)

@bp.route('/admin', methods=('GET', 'POST'))
def index():
    return render_template('admin/index.html')

def create():
    if request.method == 'POST':

        username = request.form['user_username']
        pasword = request.form['user_password']
        permissions = request.form['user_permissions']

        title = request.form['category_title']
        description = request.form['category_description']
        type = request.form['category_type']

        activity = request.form['activity_name']
        points = request.form['activity_points']
        logged_chapter = request.form['activity_chapter']

        item = request.form['spending_item']
        cost = request.form['spending_cost']
        spent_chapter = request.form['spending_chapter']

        db = get_db()
        #If a username has been provided and we're adding an account.

        db.execute(
            'INSERT INTO user (username, password, cb, pc, te, balance)'
            ' Values (?, ?, 0, 0, 0, 0)',
            (username, generate_password_hash(password))
        )
        #If a category title has been provided and we're adding categories

        db.execute(
            'INSERT INTO action_list (title, description, type)'
            ' Values (?, ?, ?)',
            (title, description, type)
        )
        #If an activity has been provided and we're logging points

        db.execute(
            'INSERT INTO action (title, points, chapter)'
            ' Values (?, ?, ?)',
            (activity, points, logged_chapter)
        )
                # # Update Chapter Building, Policy Change, or Training and Education Points on the Chapter profiles.
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
        #If an item has been provided and we're spending points

        db.execute(
            'INSERT INTO spending (title, points, author_id)'
            ' Values (?, ?, ?)',
            (item, cost, spent_chapter)
        )
        db.commit()
    return redirect(url_for('admin.index'))
    return render_template('admin/index.html')
