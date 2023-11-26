import os
from flask import Blueprint, Flask, render_template, send_from_directory

def page_not_found(e):
    return render_template('evni.html', error='404 : Page introuvable'), 404

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
    
    app.register_error_handler(404, page_not_found)

    from . import db
    db.init_app(app)

    from . import user
    app.register_blueprint(user.bp)

    # Note: if possible just serve the static files with Nginx or something
    cssbp = Blueprint('css', __name__, static_url_path='/css', static_folder='static/css')
    imgbp = Blueprint('img', __name__, static_url_path='/img', static_folder='static/img')
    jsbp = Blueprint('js', __name__, static_url_path='/js', static_folder='static/js')
    goodiesbp = Blueprint('goodies', __name__, static_url_path='/goodies', static_folder='static/goodies')
    swfbp = Blueprint('swf', __name__, static_url_path='/swf', static_folder='static/swf')
    app.register_blueprint(cssbp)
    app.register_blueprint(imgbp)
    app.register_blueprint(jsbp)
    app.register_blueprint(goodiesbp)
    app.register_blueprint(swfbp)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    return app
