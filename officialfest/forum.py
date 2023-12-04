import dateutil.parser
from . import utils
from flask import Blueprint, redirect, render_template, request
from officialfest.db import get_db
from babel.dates import format_datetime
from datetime import datetime
from itertools import chain

bp = Blueprint('forum', __name__, url_prefix='/forum.html')

THREADS_PER_PAGE = 15
MESSAGES_PER_PAGE = 10
ALLOWED_PICTOS = list(chain(range(115), range(116, 118), range(1000, 1186), range(1190, 1239)))

@bp.app_template_filter('pretty_thread_date')
def pretty_thread_date_filter(date: datetime) -> str:
    # TODO: translations
    return format_datetime(date, 'EEEE dd LLLL YYYY', locale='fr_FR')

@bp.app_template_filter('pretty_message_date')
def pretty_thread_date_filter(date_str: str) -> str:
    date = dateutil.parser.parse(date_str)
    # TODO: translations
    return format_datetime(date, 'EEEE dd LLL YYYY HH:mm', locale='fr_FR')

@bp.route('/', methods=['GET'], strict_slashes=False)
def get_forum():
    db = get_db()
    # Fetch all themes
    themes = db.execute('SELECT theme_id, name, description \
                         FROM forum_themes \
                         WHERE is_restricted = 0 \
                         ORDER BY theme_id ASC').fetchall()
    return render_template('forum/forum.html', themes=themes)

@bp.route('/theme/<int:theme_id>/', methods=['GET'], strict_slashes=False)
def get_theme(theme_id):
    args = utils.args_from_query_string(request.query_string)
    db = get_db()
    # Fetch theme
    theme = db.execute('SELECT forum_themes.*, COUNT(*) AS "total_threads" \
                        FROM forum_themes LEFT OUTER JOIN forum_threads USING (theme_id) \
                        WHERE theme_id = ?', (theme_id,)).fetchone()
    if theme['theme_id'] is None:
        # TODO: translations
        return render_template('evni.html', error='404 : Thème introuvable'), 404
    # TODO: allow access to restricted area
    if theme['is_restricted']:
        # TODO: translations
        return render_template('evni.html', error='403 : Accès interdit'), 403
    # Fetch sticky threads
    sticky_threads = db.execute('SELECT forum_threads.*, users.user_id AS "author_id", users.username AS "author_name", users.is_moderator AS "author_is_moderator" \
                                 FROM forum_threads INNER JOIN users ON forum_threads.author = users.user_id \
                                 WHERE theme_id = ? AND is_sticky = 1 \
                                 ORDER BY thread_id ASC', (theme_id,)).fetchall()
    # Fetch page of threads to show
    total_threads = theme['total_threads']
    max_page = 1 + ((total_threads - len(sticky_threads) - 1) // THREADS_PER_PAGE)
    page = utils.sanitized_page_arg(args, max_page)
    latest_threads = db.execute('WITH latest_messages AS ( \
                                     SELECT thread_id, MAX(forum_messages.message_id) AS "last_message_id", forum_messages.created_at AS "last_message_date" \
                                     FROM forum_messages INNER JOIN forum_threads USING (thread_id) \
                                     WHERE theme_id = ? AND forum_threads.is_sticky = 0\
                                     GROUP BY thread_id \
                                 ) \
                                 SELECT forum_threads.*, users.user_id AS "author_id", users.username AS "author_name", users.is_moderator AS "author_is_moderator", last_message_date \
                                 FROM forum_threads INNER JOIN users ON forum_threads.author = users.user_id INNER JOIN latest_messages USING (thread_id) \
                                 ORDER BY last_message_id DESC \
                                 LIMIT ? OFFSET ?', (theme_id, THREADS_PER_PAGE, THREADS_PER_PAGE * (page - 1))).fetchall()
    # Group threads by day of last message
    latest_threads_by_day = []
    curr_date = datetime(1, 1, 1)
    for thread in latest_threads:
        date = dateutil.parser.parse(thread['last_message_date'])
        if (date.day, date.month, date.year) != (curr_date.day, curr_date.month, curr_date.year):
            latest_threads_by_day.append((date,[thread]))
            curr_date = date
        else:
            latest_threads_by_day[-1][1].append(thread)
    return render_template('forum/theme.html', theme=theme, page=page, max_page=max_page,
                           sticky_threads=sticky_threads, latest_threads_by_day=latest_threads_by_day)

@bp.route('/thread/<int:thread_id>/', methods=['GET'], strict_slashes=False)
def get_thread(thread_id):
    args = utils.args_from_query_string(request.query_string)
    db = get_db()
    # Fetch thread
    thread = db.execute('SELECT forum_threads.*, forum_themes.name AS "theme_name", forum_themes.is_restricted, COUNT(*) AS "messages_count" \
                         FROM forum_threads INNER JOIN forum_themes USING (theme_id) INNER JOIN forum_messages USING (thread_id) \
                         WHERE thread_id = ?', (thread_id,)).fetchone()
    if thread['thread_id'] is None:
        # TODO: translations
        return render_template('evni.html', error='404 : Thread introuvable'), 404
    # TODO: allow access to restricted area
    if thread['is_restricted']:
        # TODO: translations
        return render_template('evni.html', error='403 : Accès interdit'), 403
    # Fetch page of messages to show
    messages_count = thread['messages_count']
    max_page = 1 + ((messages_count - 2) // MESSAGES_PER_PAGE)
    page = utils.sanitized_page_arg(args, max_page)
    messages = db.execute('SELECT forum_messages.*, users.username AS "author_name", users.pyramid_step AS "author_pyramid_step", users.pyramid_rank as "author_pyramid_rank", users.has_carrot AS "author_has_carrot", \
                           users.is_moderator AS "author_is_moderator", users.is_admin AS "author_is_admin" \
                           FROM forum_messages INNER JOIN users ON (forum_messages.author = users.user_id) \
                           WHERE thread_id = ? \
                           ORDER BY forum_messages.message_id ASC \
                           LIMIT ? OFFSET ?', (thread_id, MESSAGES_PER_PAGE + (1 if page == 1 else 0), MESSAGES_PER_PAGE * (page - 1) + (1 if page > 1 else 0))).fetchall()
    return render_template('forum/thread.html', thread=thread, page=page, max_page=max_page, messages=messages)

@bp.route('/message/<int:message_id>/', methods=['GET'], strict_slashes=False)
def get_message(message_id):
    db = get_db()
    # Fetch thread containing message
    thread = db.execute('SELECT forum_threads.*, forum_themes.name AS "theme_name", forum_themes.is_restricted, COUNT(*) AS "messages_count" \
                         FROM forum_messages INNER JOIN forum_threads USING (thread_id) INNER JOIN forum_themes USING (theme_id) \
                         WHERE thread_id = (SELECT thread_id FROM forum_messages WHERE message_id = ?)', (message_id,)).fetchone()
    if thread['thread_id'] is None:
        # TODO: translations
        return render_template('evni.html', error='404 : Message introuvable'), 404
    # TODO: allow access to restricted area
    if thread['is_restricted']:
        # TODO: translations
        return render_template('evni.html', error='403 : Accès interdit'), 403
    # Fetch message rank in thread
    message_rank = db.execute('SELECT COUNT(*) \
                               FROM forum_messages \
                               WHERE thread_id = ? AND message_id < ? \
                               ORDER BY message_id ASC', (thread['thread_id'], message_id)).fetchone()[0]
    # Fetch page of messages to show
    page = 1 + ((message_rank - 1) // MESSAGES_PER_PAGE)
    messages_count = thread['messages_count']
    max_page = 1 + ((messages_count - 2) // MESSAGES_PER_PAGE)
    messages = db.execute('SELECT forum_messages.*, users.username AS "author_name", users.pyramid_step AS "author_pyramid_step", users.pyramid_rank as "author_pyramid_rank", users.has_carrot AS "author_has_carrot", \
                           users.is_moderator AS "author_is_moderator", users.is_admin AS "author_is_admin" \
                           FROM forum_messages INNER JOIN users ON (forum_messages.author = users.user_id) \
                           WHERE thread_id = ? \
                           ORDER BY forum_messages.message_id ASC \
                           LIMIT ? OFFSET ?', (thread['thread_id'], MESSAGES_PER_PAGE + (1 if page == 1 else 0), MESSAGES_PER_PAGE * (page - 1) + (1 if page > 1 else 0))).fetchall()
    return render_template('forum/thread.html', thread=thread, page=page, max_page=max_page, messages=messages)

@bp.route('/theme/<int:theme_id>/createThreadForm', methods=['GET'])
def get_createThreadForm(theme_id):
    db = get_db()
    # Fetch theme
    theme = db.execute('SELECT * \
                        FROM forum_themes \
                        WHERE theme_id = ?', (theme_id,)).fetchone()
    if theme is None:
        # TODO: translations
        return render_template('evni.html', error='404 : Thème introuvable'), 404
    # TODO: allow access to restricted area
    if theme['is_restricted']:
        # TODO: translations
        return render_template('evni.html', error='403 : Accès interdit'), 403
    return render_template('forum/createThreadForm.html', theme=theme, pictos=ALLOWED_PICTOS)

@bp.route('/theme/<int:theme_id>/createThread', methods=['POST'])
def post_createThread(theme_id):
    return redirect('/')

@bp.route('/thread/<int:thread_id>/replyForm', methods=['GET'])
def get_replyForm(thread_id):
    db = get_db()
    # Fetch theme
    thread = db.execute('SELECT forum_threads.*, forum_themes.is_restricted, forum_themes.name AS "theme_name" \
                        FROM forum_threads INNER JOIN forum_themes USING (theme_id) \
                        WHERE thread_id = ?', (thread_id,)).fetchone()
    if thread is None:
        # TODO: translations
        return render_template('evni.html', error='404 : Thread introuvable'), 404
    # TODO: allow access to restricted area
    if thread['is_restricted']:
        # TODO: translations
        return render_template('evni.html', error='403 : Accès interdit'), 403
    message = db.execute('SELECT forum_messages.*, users.username AS "author_name", users.pyramid_step AS "author_pyramid_step", users.pyramid_rank as "author_pyramid_rank", users.has_carrot AS "author_has_carrot", \
                           users.is_moderator AS "author_is_moderator", users.is_admin AS "author_is_admin" \
                           FROM forum_messages INNER JOIN users ON (forum_messages.author = users.user_id) \
                           WHERE thread_id = ? \
                           ORDER BY forum_messages.message_id ASC \
                           LIMIT 1', (thread_id,)).fetchone()
    return render_template('forum/replyForm.html', thread=thread, pictos=ALLOWED_PICTOS, message=message)

@bp.route('/thread/<int:thread_id>/reply', methods=['POST'])
def post_reply(thread_id):
    return redirect('/')

@bp.route('/redirect', methods=['GET'])
def get_redirect():
    url = request.args.get('url')
    if url is None:
        return redirect('/')
    # TODO: check current website lang before replacing
    elif url.startswith('http://www.hammerfest.fr'):
        return redirect(url.replace('http://www.hammerfest.fr', ''))
    else:
        return redirect(url)

@bp.route('/search', methods=['GET'])
def get_search():
    return render_template('evni.html', error='501 : Pas encore implémenté'), 501
