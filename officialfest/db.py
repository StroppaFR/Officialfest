import click
import sqlite3
from flask import current_app, g
from itertools import chain

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    # Add all quests and items for user with id 0
    for quest_id in range(76):
        db.execute('INSERT INTO user_quests (user_id, quest_id, completed) \
                    VALUES (0, ?, 1)', (quest_id,))
    for item_id in chain(range(115), range(116, 118)): # No casque de volleyfest
        db.execute('INSERT INTO user_unlocked_items (user_id, item_id) \
                    VALUES (0, ?)', (item_id,))
    for item_id in chain(range(1000, 1186), range(1190, 1239)): # No forbidden item
        db.execute('INSERT INTO user_unlocked_items (user_id, item_id) \
                    VALUES (0, ?)', (item_id,))
    db.commit()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
