import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    db.execute(
        'INSERT INTO user (username, password, email, permissions, cb, pc, te, balance, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        ('admin', generate_password_hash('admin'), 'tyler@ssdp.org', 'Admin', 0, 0 ,0 , 0, 'admin')
    )
    db.commit()
    # I couldn't figure out how to make another click command
    # So I've just been cannabilizing this function to mege the old database
    # old_users = db.execute('SELECT * from dr_users').fetchall()
    # for user in old_users:
    #     db.execute(
    #         'INSERT INTO user (username, password, email, permissions, cb, pc, te, balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    #         (user['field2'], generate_password_hash('meowcatgrassroots'), user['field4'], 'Chapter', 0, 0 ,0 , 0))
    # db.commit()
    # Here's the code to merge the old categories
    # old_categories = db.execute('SELECT * from dr_taxonomy_term_data').fetchall()
    # for category in old_categories:
    #     db.execute(
    #         'INSERT INTO action_list (title, description, type) VALUES (?, ?, ?)',
    #         (category['field3'], category['field4'], 'Policy Change'))
    # db.commit()
    # More bastardization of this function - updating URLS en masse
    # chapters = db.execute('SELECT * from user').fetchall()
    # for chapter in chapters:
    #     url = chapter['username'].replace(' ', '-').lower()
    #     db.execute('UPDATE user set url = ? WHERE username = ?', (url, chapter['username'],))
    # db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
