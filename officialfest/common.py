import dateutil.parser
from flask import Blueprint, redirect, request, render_template
from flask_babel import format_datetime

bp = Blueprint('common', __name__, url_prefix='/')

@bp.app_template_filter('pretty_score')
def pretty_score_filter(score: int) -> str:
    return f'{score:,}'.replace(',', '.')

@bp.app_template_filter('pretty_hof_date')
def pretty_hof_date_filter(date) -> str:
    if isinstance(date, str):
        date = dateutil.parser.parse(date)
    return format_datetime(date, 'YYYY-MM-dd')

@bp.route('/', methods=['GET'])
@bp.route('/index.html', methods=['GET'])
def get_index():
    return render_template('common/index.html')

@bp.route('/login.html/logout', methods=['GET'])
def get_logout():
    return redirect('/')

@bp.route('/intro.html', methods=['GET'])
def get_intro():
    return render_template('common/intro.html')

@bp.route('/try.html', methods=['GET'])
def get_try():
    return render_template('common/try.html')

@bp.route('/guide.html', methods=['GET'])
def get_guide():
    return render_template('common/guide.html')

@bp.route('/shop.html', methods=['GET'])
def get_shop():
    return render_template('common/shop.html')

@bp.route('/play.html', methods=['GET'])
def get_play():
    return render_template('common/play.html')

@bp.route('/play.html/credits', methods=['GET'])
def get_credits():
    return render_template('common/credits.html')

@bp.route('/play.html/<mode>', methods=['POST'])
def post_play_mode(mode):
    if mode not in ['solo', 'timeattack', 'multi']:
        return render_template('evni.html', error='404 : Mode introuvable'), 404
    if mode == 'multi':
        mode = 'multicoop'
    options = ','.join(request.form.getlist('options[]'))
    return render_template('common/play_mode.html', mode=mode, options=options)

@bp.route('/soccer.html', methods=['POST'])
def post_soccer():
    level = request.form.get('level')
    if level not in ['set_soc_0', 'set_soc_1', 'set_soc_2', 'set_soc_3']:
        return render_template('evni.html', error='404 : Terrain introuvable'), 404
    options = ','.join(request.form.getlist('options[]'))
    options += ',' + level
    return render_template('common/soccer.html', options=options)
