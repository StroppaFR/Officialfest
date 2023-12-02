import os
from flask import Blueprint, send_from_directory

# Note: if possible, serve all the static files using Nginx for better performances
bp = Blueprint('static', __name__, url_prefix='/')

cssbp = Blueprint('css', __name__, static_url_path='/css', static_folder='static/css')
imgbp = Blueprint('img', __name__, static_url_path='/img', static_folder='static/img')
jsbp = Blueprint('js', __name__, static_url_path='/js', static_folder='static/js')
goodiesbp = Blueprint('goodies', __name__, static_url_path='/goodies', static_folder='static/goodies')
swfbp = Blueprint('swf', __name__, static_url_path='/swf', static_folder='static/swf')
    
bp.register_blueprint(cssbp)
bp.register_blueprint(imgbp)
bp.register_blueprint(jsbp)
bp.register_blueprint(goodiesbp)
bp.register_blueprint(swfbp)

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(bp.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@bp.route('/play.html/creditsSwf')
def get_creditsSwf():
    return send_from_directory(os.path.join(bp.root_path, 'static', 'swf'), 'credits.swf', mimetype='application/x-shockwave-flash')
