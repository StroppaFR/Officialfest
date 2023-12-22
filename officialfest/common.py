import dateutil.parser
from flask import Blueprint, current_app, redirect, request, render_template
from flask_babel import format_datetime, gettext

bp = Blueprint('common', __name__, url_prefix='/')

@bp.app_template_filter('pretty_score')
def pretty_score_filter(score: int) -> str:
    return f'{score:,}'.replace(',', '.')

@bp.app_template_filter('pretty_hof_date')
def pretty_hof_date_filter(date) -> str:
    if isinstance(date, str):
        date = dateutil.parser.parse(date)
    return format_datetime(date, 'yyyy-MM-dd')

@bp.app_context_processor
def inject_lang():
    return dict(LANG=current_app.config['LANG'])

@bp.app_context_processor
def inject_websites_urls():
    return dict(HAMMERFEST_FR_URL=current_app.config['HAMMERFEST_FR_URL'], HAMMERFEST_ES_URL=current_app.config['HAMMERFEST_ES_URL'], HAMMERFEST_EN_URL=current_app.config['HAMMERFEST_EN_URL'])

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
    if current_app.config.get('LANG') == 'es':
        return render_template('common/guide_es.html')
    elif current_app.config.get('LANG') == 'en':
        return render_template('common/guide_en.html')
    else:
        return render_template('common/guide_fr.html')


@bp.route('/shop.html', methods=['GET'])
def get_shop():
    return render_template('common/shop.html')

@bp.route('/play.html', methods=['GET'])
def get_play():
    # TODO: add missing en version of the play page
    if current_app.config.get('LANG') == 'es':
        return render_template('common/play_es.html')
    else:
        return render_template('common/play_fr.html')

@bp.route('/play.html/credits', methods=['GET'])
def get_credits():
    return render_template('common/credits.html')

@bp.route('/play.html/<mode>', methods=['POST'])
def post_play_mode(mode):
    if mode not in ['solo', 'timeattack', 'multi']:
        return render_template('evni.html', error=gettext(u'404 : Mode %(mode)s introuvable', mode=mode)), 404
    if mode == 'multi':
        mode = 'multicoop'
    options = ','.join(request.form.getlist('options[]'))
    return render_template('common/play_mode.html', mode=mode, options=options)

@bp.route('/soccer.html', methods=['POST'])
def post_soccer():
    level = request.form.get('level')
    if level not in ['set_soc_0', 'set_soc_1', 'set_soc_2', 'set_soc_3']:
        return render_template('evni.html', error=gettext('404 : Terrain %(level)s introuvable', level=level)), 404
    options = ','.join(request.form.getlist('options[]'))
    options += ',' + level
    return render_template('common/soccer.html', options=options)
