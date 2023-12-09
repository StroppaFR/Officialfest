from . import utils
from flask import Blueprint, current_app, render_template, request
from officialfest.db import get_db

bp = Blueprint('scores', __name__, url_prefix='/')

@bp.route('/scores.html', methods=['GET'])
@bp.route('/scores.html/mypos', methods=['GET'])
def get_scores():
    SCORES_RISING_USERS_PER_PYRAMID_STEP = current_app.config['SCORES_RISING_USERS_PER_PYRAMID_STEP']
    LEAGUES_PARAM = current_app.config['LEAGUES_PARAM']
    SCORES_PER_PAGE = current_app.config['SCORES_PER_PAGE']

    args = utils.args_from_query_string(request.query_string)
    db = get_db()
    try:
        pyramid_step = min(4, max(1, int(args['id'])))
    except Exception as e:
        pyramid_step = 1
    # Count scores at this pyramid step
    total_scores = db.execute('SELECT COUNT(*) AS "total_scores" \
                               FROM user_weekly_scores INNER JOIN users USING (user_id) \
                               WHERE pyramid_step = ?', (pyramid_step,)).fetchone()[0]
    max_page = 1 + ((total_scores - 1) // SCORES_PER_PAGE)
    page = utils.sanitized_page_arg(args, max_page)
    # Get scores to display
    scores = db.execute('SELECT user_weekly_scores.*, users.username \
                         FROM user_weekly_scores INNER JOIN users USING (user_id) \
                         WHERE pyramid_step = ? \
                         ORDER BY weekly_score DESC \
                         LIMIT ? OFFSET ?', (pyramid_step, SCORES_PER_PAGE, SCORES_PER_PAGE * (page - 1))).fetchall()
    # Calculate score to beat
    score_to_beat = db.execute('SELECT weekly_score \
                                FROM user_weekly_scores INNER JOIN users USING (user_id) \
                                WHERE pyramid_step = ? \
                                ORDER BY weekly_score DESC \
                                LIMIT ?', (pyramid_step, SCORES_RISING_USERS_PER_PYRAMID_STEP[pyramid_step])).fetchall()
    try:
        score_to_beat = score_to_beat[-1][0]
    except Exception as e:
        score_to_beat = 0
    # Get latest hof message
    hof_message = db.execute('SELECT hof_messages.*, users.username \
                              FROM hof_messages INNER JOIN users ON hof_messages.author = users.user_id \
                              ORDER BY written_at DESC \
                              LIMIT 1').fetchone()
    return render_template('scores/scores.html', pyramid_step=pyramid_step, scores=scores, page=page, max_page=max_page,
                           score_to_beat=score_to_beat, leagues_param=LEAGUES_PARAM, hof_message=hof_message)

@bp.app_template_filter('pretty_timeattack_score')
def pretty_score_filter(milliseconds: int) -> str:
    res = ''
    if milliseconds < 0:
        milliseconds = -milliseconds
        res += '-'
    minutes = milliseconds // (60 * 1000)
    milliseconds -= 1000 * 60 * minutes
    seconds = milliseconds // 1000
    milliseconds -= 1000 * seconds
    res += f'{minutes}" {seconds:02d}\' {milliseconds}'
    return res

@bp.route('/scores.html/timeattack', methods=['GET'])
def get_timeattack_scores():
    SCORES_PER_PAGE = current_app.config['SCORES_PER_PAGE']

    args = utils.args_from_query_string(request.query_string)
    db = get_db()
    # Count scores
    total_scores = db.execute('SELECT COUNT(*) AS "total_scores" \
                               FROM user_timeattack_scores').fetchone()[0]
    max_page = 1 + ((total_scores - 1) // SCORES_PER_PAGE)
    page = utils.sanitized_page_arg(args, max_page)
    # Get scores to display
    scores = db.execute('SELECT user_timeattack_scores.*, users.username \
                         FROM user_timeattack_scores INNER JOIN users USING (user_id) \
                         ORDER BY milliseconds ASC \
                         LIMIT ? OFFSET ?', (SCORES_PER_PAGE, SCORES_PER_PAGE * (page - 1))).fetchall()
    return render_template('scores/timeattack.html', page=page, max_page=max_page, scores=scores)

@bp.route('/halloffame.html', methods=['GET'])
def get_halloffame():
    SCORES_RISING_USERS_PER_PYRAMID_STEP = current_app.config['SCORES_RISING_USERS_PER_PYRAMID_STEP']
    LEAGUES_PARAM = current_app.config['LEAGUES_PARAM']
    SCORES_PER_PAGE = current_app.config['SCORES_PER_PAGE']

    args = utils.args_from_query_string(request.query_string)
    db = get_db()
    # Count messages
    total_messages = db.execute('SELECT COUNT(*) AS "total_messages" \
                               FROM hof_messages').fetchone()[0]
    max_page = 1 + ((total_messages - 1) // SCORES_PER_PAGE)
    page = utils.sanitized_page_arg(args, max_page)
    # Get messages to display
    messages = db.execute('SELECT hof_messages.*, users.username \
                         FROM hof_messages INNER JOIN users ON hof_messages.author = users.user_id \
                         ORDER BY written_at DESC \
                         LIMIT ? OFFSET ?', (SCORES_PER_PAGE, SCORES_PER_PAGE * (page - 1))).fetchall()
    # Get latest hof message
    last_hof_message = db.execute('SELECT hof_messages.*, users.username \
                              FROM hof_messages INNER JOIN users ON hof_messages.author = users.user_id \
                              ORDER BY written_at DESC \
                              LIMIT 1').fetchone()
    return render_template('scores/halloffame.html', page=page, max_page=max_page, messages=messages,
                           leagues_param=LEAGUES_PARAM, last_hof_message=last_hof_message)
