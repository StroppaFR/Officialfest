import dateutil.parser
from babel.dates import format_datetime
from flask import Blueprint, render_template

bp = Blueprint('common', __name__, url_prefix='/')

@bp.app_template_filter('pretty_score')
def pretty_score_filter(score: int) -> str:
    return f'{score:,}'.replace(',', '.')

@bp.app_template_filter('pretty_hof_date')
def pretty_hof_date_filter(date_str: str) -> str:
    date = dateutil.parser.parse(date_str)
    # TODO: handle other locales
    return format_datetime(date, 'YYYY-MM-dd', locale='fr_FR')

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
