import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    app.config.from_pyfile('config.py', silent=True)


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    app.add_url_rule('/leaderboard', endpoint='leaderboard')
    app.add_url_rule('/available-activities', endpoint='availableActivities')
    app.add_url_rule('/faq', endpoint='faq')
    app.add_url_rule('/store', endpoint='store')


    from . import chapters
    app.register_blueprint(chapters.bp)
    app.add_url_rule('/chapters', endpoint='index')

    from . import admin
    app.register_blueprint(admin.bp)
    app.add_url_rule('/admin', endpoint='index')

    return app

app = create_app()
