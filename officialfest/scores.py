from . import utils
from flask import Blueprint, render_template, request
from officialfest.db import get_db

bp = Blueprint('scores', __name__, url_prefix='/')

SCORES_PER_PYRAMID_PAGE = 30
# TODO: this is server dependant
RISING_USERS_PER_STEP = {1: 1, 2: 10, 3: 100, 4: 1000}

@bp.route('/scores.html', methods=['GET'])
@bp.route('/scores.html/mypos', methods=['GET'])
def get_scores():
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
    max_page = 1 + ((total_scores - 1) // SCORES_PER_PYRAMID_PAGE)
    page = utils.sanitized_page_arg(args, max_page)
    # Get scores to display
    scores = db.execute('SELECT user_weekly_scores.*, users.username \
                         FROM user_weekly_scores INNER JOIN users USING (user_id) \
                         WHERE pyramid_step = ? \
                         ORDER BY weekly_score DESC \
                         LIMIT ? OFFSET ?', (pyramid_step, SCORES_PER_PYRAMID_PAGE, SCORES_PER_PYRAMID_PAGE * (page - 1))).fetchall()
    # Calculate score to beat
    score_to_beat = db.execute('SELECT weekly_score \
                                FROM user_weekly_scores INNER JOIN users USING (user_id) \
                                WHERE pyramid_step = ? \
                                ORDER BY weekly_score DESC \
                                LIMIT ?', (pyramid_step, RISING_USERS_PER_STEP[pyramid_step])).fetchall()
    try:
        score_to_beat = score_to_beat[-1][0]
    except Exception as e:
        score_to_beat = 0
    # Get latest hof message
    hof_message = db.execute('SELECT hof_messages.*, users.username \
                              FROM hof_messages INNER JOIN users ON hof_messages.author = users.user_id \
                              ORDER BY written_at DESC \
                              LIMIT 1').fetchone()
    leagues_param = '|'.join(str(v) for v in sorted(RISING_USERS_PER_STEP.values()))
    return render_template('scores/scores.html', pyramid_step=pyramid_step, scores=scores, page=page, max_page=max_page, score_to_beat=score_to_beat, leagues_param=leagues_param, hof_message=hof_message)
