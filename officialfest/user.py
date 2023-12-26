from flask import Blueprint, redirect, render_template
from flask_babel import gettext
from itertools import chain
from officialfest.db import get_db
from officialfest.items_data import ALL_ITEMS, ALL_QUESTS, ALL_FAMILIES

bp = Blueprint('user', __name__, url_prefix='/user.html')

@bp.app_context_processor
def inject_all_items():
    return dict(ALL_ITEMS=ALL_ITEMS)

@bp.app_context_processor
def inject_all_quests():
    return dict(ALL_QUESTS=ALL_QUESTS)

@bp.app_context_processor
def inject_all_families():
    return dict(ALL_FAMILIES=ALL_FAMILIES)

@bp.route('/', methods=['GET'], strict_slashes=False)
def get_user_account():
    return render_template('user/user-account.html')

@bp.route('/godChildren', methods=['GET'])
def get_godChildren():
    return render_template('user/godChildren.html')

@bp.route('/changeEmail', methods=['POST'])
@bp.route('/changeEmailPublic', methods=['POST'])
@bp.route('/passwd', methods=['POST'])
@bp.route('/raz', methods=['POST'])
@bp.route('/unsubscribe', methods=['POST'])
def post_update_user():
    return redirect('/user.html')

@bp.route('/<int:user_id>/', methods=['GET'], strict_slashes=False)
def show_profile(user_id):
    db = get_db()
    # Fetch user information
    user = db.execute('SELECT users.*, hof_messages.message as "hof_message", hof_messages.written_at as "hof_message_date", user_weekly_scores.weekly_score \
                       FROM users LEFT OUTER JOIN hof_messages ON user_id = author LEFT OUTER JOIN user_weekly_scores USING (user_id) \
                       WHERE user_id = ?', (user_id,)).fetchone()
    if user is None:
        return render_template('evni.html', error=gettext('404 : Utilisateur introuvable')), 404
    # Fetch user quests
    user_quests = db.execute('SELECT quest_id, completed \
                              FROM user_quests INNER JOIN users USING (user_id) \
                              WHERE user_id = ?', (user_id,)).fetchall()
    completed_quests = []
    current_quests = []
    for user_quest in user_quests:
        quest_id = user_quest['quest_id']
        if user_quest['completed']:
            completed_quests.append(quest_id)
        else:
            current_quests.append(quest_id)
    # Fetch user unlocked items
    user_unlocked_items = db.execute('SELECT item_id \
                              FROM user_unlocked_items INNER JOIN users USING (user_id) \
                              WHERE user_id = ?', (user_id,)).fetchall()
    user_items = set(item['item_id'] for item in user_unlocked_items)
    # Render the profile page
    return render_template('user/user.html', user=user, user_items=user_items,
                           completed_quests=completed_quests, current_quests=current_quests)

@bp.route('/inventory', methods=['GET'])
def get_inventory():
    return render_template('user/inventory.html')

@bp.route('/quests', methods=['GET'])
def get_quests():
    return render_template('user/quests.html')
