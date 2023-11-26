from flask import Blueprint, render_template

bp = Blueprint('common', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
@bp.route('/index.html', methods=['GET'])
def get_index():
    return render_template('common/index.html')

@bp.route('/intro.html', methods=['GET'])
def get_intro():
    return render_template('common/intro.html')

@bp.route('/guide.html', methods=['GET'])
def get_guide():
    return render_template('common/guide.html')
