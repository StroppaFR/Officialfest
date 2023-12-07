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

MAX_SEARCH_STRINGS = 5
MAX_SEARCH_RESULTS = 1000
MIN_SEARCH_DATE = datetime.strptime("2006-02-27", "%Y-%m-%d")
MAX_SEARCH_DATE = datetime.strptime("2023-12-31", "%Y-%m-%d")

@bp.app_template_filter('pretty_thread_date')
def pretty_thread_date_filter(date) -> str:
    if isinstance(date, str):
        date = dateutil.parser.parse(date)
    # TODO: translations
    return format_datetime(date, 'EEEE dd LLLL YYYY', locale='fr_FR')

@bp.app_template_filter('pretty_message_date')
def pretty_thread_date_filter(date) -> str:
    if isinstance(date, str):
        date = dateutil.parser.parse(date)
    # TODO: translations
    return format_datetime(date, 'EEEE dd LLL YYYY HH:mm', locale='fr_FR')

@bp.app_template_filter('short_date')
def pretty_thread_date_filter(date) -> str:
    if isinstance(date, str):
        date = dateutil.parser.parse(date)
    # TODO: translations
    return format_datetime(date, 'dd LLL YYYY', locale='fr_FR')

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
    elif url.startswith('http://www.hammerfest.es'):
        return redirect(url.replace('http://www.hammerfest.es', ''))
    elif url.startswith('http://www.hfest.net'):
        return redirect(url.replace('http://www.hfest.net', ''))
    else:
        return redirect(url)

@bp.route('/search', methods=['GET'])
def get_search():
    search_arg = request.args.get("search")
    author_arg = request.args.get("author")
    from_date_arg = request.args.get("from_date")
    to_date_arg = request.args.get("to_date")

    # If no parameters is supplied, render default search page
    if not search_arg and not author_arg and not from_date_arg and not to_date_arg:
        return render_template('forum/search.html', min_date=MIN_SEARCH_DATE.strftime("%Y-%m-%d"), max_date=MAX_SEARCH_DATE.strftime("%Y-%m-%d"))

    # Parse date arguments
    from_date = MIN_SEARCH_DATE
    to_date = MAX_SEARCH_DATE
    try:
        from_date = dateutil.parser.parse(from_date_arg)
    except Exception as e:
        pass
    try:
        to_date = dateutil.parser.parse(to_date_arg)
    except Exception as e:
        pass
    to_date = to_date.replace(hour=23, minute=59, second=59)

    db = get_db()
    # If author arg is supplied, first check that the user exists and get his user_id
    if author_arg:
        user_id = db.execute('SELECT user_id FROM users WHERE LOWER(username) = LOWER(?) ORDER BY user_id DESC', (author_arg,)).fetchone()
        if not user_id:
            return render_template('evni.html', error=f'404: Utilisateur {author_arg} introuvable'), 404
        else:
            user_id = user_id[0]

    inside_quotes = False
    plus = False
    minus = False
    i = 0
    curr_string = ""
    found_strings = []
    # Parse the search string according to MT rules
    for i, c in enumerate(search_arg):
        if c == '+' or c == '-':
            # + / - is part of a string
            if inside_quotes:
                curr_string += c
            else:
                # + / - ends the current string
                if curr_string:
                    found_strings.append((curr_string, plus, minus))
                    curr_string = ''
                # and sets the + / - state
                plus = c == '+'
                minus = c == '-'
        elif c == '"':
            # " ends the current string
            if curr_string:
                found_strings.append((curr_string, plus, minus))
                curr_string = ''
            # and switches inside_quotes state
            inside_quotes = not inside_quotes
            # and resets + / - state if leaving quoted string
            if not inside_quotes:
                plus = False
                minus = False
        elif c == " ":
            # space inside string
            if inside_quotes:
                curr_string += c
            else:
                # space ends the current string
                if curr_string:
                    found_strings.append((curr_string, plus, minus))
                    curr_string = ''
                # and resets + / -
                plus = False
                minus = False
        else:
            curr_string += c
    # close the last string
    if curr_string:
        found_strings.append((curr_string, plus, minus))
        curr_string = ''

    # Remove duplicates
    found_strings = set(found_strings)
    # Avoid DoS
    if len(found_strings) > MAX_SEARCH_STRINGS:
        return render_template('evni.html', error=f'403: trop de filtres dans la recherche ; merci de vous limiter à {MAX_SEARCH_STRINGS} filtres maximum !'), 403

    required_strings = [s[0] for s in found_strings if s[1]]
    forbidden_strings = [s[0] for s in found_strings if s[2]]
    optional_strings = [s[0] for s in found_strings if (not s[1] and not s[2])]

    # Build SQL prepared statement
    query = 'SELECT forum_messages.*, forum_threads.name AS "thread_name", users.user_id, users.username \
             FROM forum_messages INNER JOIN forum_threads USING (thread_id) INNER JOIN forum_themes USING (theme_id) INNER JOIN users ON forum_messages.author = users.user_id \
             WHERE (NOT forum_themes.is_restricted) '
    filter_statement_parameters = []
    # Build required filter
    if len(required_strings) > 0:
        query += 'AND (' + ' AND '.join('instr(lower(html_content), lower(?))' for _ in required_strings) + ') '
        filter_statement_parameters.extend(required_strings)
    # Build forbidden filter
    if len(forbidden_strings) > 0:
        query += ' AND (' + ' AND '.join('NOT instr(lower(html_content), lower(?))' for _ in forbidden_strings) + ') '
        filter_statement_parameters.extend(forbidden_strings)
    # Build optional filter. It is useless if there is any required string
    if len(required_strings) == 0 and len(optional_strings) > 0:
        query += ' AND (' + ' OR '.join('instr(lower(html_content), lower(?))' for _ in optional_strings) + ') '
        filter_statement_parameters.extend(optional_strings)
    assert len(filter_statement_parameters) == query.count('?')

    # Add author filter
    if author_arg:
        query += ' AND forum_messages.author = ? '
        filter_statement_parameters.append(user_id)

    # Add date filters
    query += ' AND forum_messages.created_at <= ? AND forum_messages.created_at >= ?'
    filter_statement_parameters.append(to_date)
    filter_statement_parameters.append(from_date)

    query += ' ORDER BY message_id DESC LIMIT ?'
    filter_statement_parameters.append(MAX_SEARCH_RESULTS)
    results = db.execute(query, filter_statement_parameters).fetchall()

    return render_template('forum/search_results.html', results=results, search_arg=search_arg, author_arg=author_arg, from_date=from_date, to_date=to_date,
                           max_results=MAX_SEARCH_RESULTS, max_reached=(len(results) == MAX_SEARCH_RESULTS))
