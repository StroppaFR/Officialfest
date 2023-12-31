import os
from flask import Flask, render_template
from flask_babel import Babel, gettext
from officialfest import items_data

def page_not_found(e):
    return render_template('evni.html', error=gettext('404 : Page introuvable')), 404

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'officialfest.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # load items data before everything else
    items_data.load_data(app, app.config['LANG'])
    
    app.register_error_handler(404, page_not_found)

    from . import db
    db.init_app(app)

    from . import common
    app.register_blueprint(common.bp)

    from . import user
    app.register_blueprint(user.bp)

    from . import forum
    app.register_blueprint(forum.bp)

    from . import scores
    app.register_blueprint(scores.bp)

    from . import static
    app.register_blueprint(static.bp)

    babel = Babel(app, locale_selector=lambda: app.config['LOCALE'])

    return app
