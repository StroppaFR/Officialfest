DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS hof_messages;
DROP TABLE IF EXISTS user_unlocked_items;
DROP TABLE IF EXISTS user_quests;
DROP TABLE IF EXISTS hof_messages;
DROP TABLE IF EXISTS forum_themes;
DROP TABLE IF EXISTS forum_threads;
DROP TABLE IF EXISTS forum_posts;

CREATE TABLE users (
    user_id INTEGER NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT,
    best_score INTEGER NOT NULL DEFAULT 0,
    weekly_best_score INTEGER NOT NULL DEFAULT 0,
    best_level INTEGER DEFAULT NULL,
    has_carrot BOOLEAN NOT NULL DEFAULT FALSE,
    pyramid_step INTEGER NOT NULL DEFAULT 4,
    is_moderator BOOLEAN NOT NULL DEFAULT FALSE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE hof_messages (
    author INTEGER NOT NULL PRIMARY KEY,
    message TEXT NOT NULL,
    written_at DATETIME NOT NULL,
    FOREIGN KEY (author) REFERENCES users (user_id)
);

CREATE TABLE user_unlocked_items (
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE user_quests (
    user_id INTEGER NOT NULL,
    quest_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user_id, quest_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE forum_themes (
    theme_id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    is_restricted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE forum_threads (
    thread_id INTEGER NOT NULL PRIMARY KEY,
    theme_id INTEGER NOT NULL,
    author INTEGER NOT NULL,
    name TEXT NOT NULL,
    total_messages INTEGER NOT NULL DEFAULT 1,
    is_sticky BOOLEAN NOT NULL DEFAULT FALSE,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (theme_id) REFERENCES forum_themes (theme_id),
    FOREIGN KEY (author) REFERENCES users (user_id)
);

CREATE TABLE forum_posts (
    post_id INTEGER NOT NULL PRIMARY KEY,
    thread_id INTEGER NOT NULL,
    author INTEGER NOT NULL,
    html_content TEXT NOT NULL,
    created_at DATETIME not NULL,
    FOREIGN KEY (thread_id) REFERENCES forum_threads (thread_id),
    FOREIGN KEY (author) REFERENCES users (user_id)
);

INSERT INTO users (user_id, username, email, best_score, weekly_best_score, best_level, has_carrot, pyramid_step, is_moderator, is_admin)
VALUES (1, 'Igor', 'igor@hammerfest.fr', 19001234, 456789, 114, TRUE, 0, TRUE, FALSE);
INSERT INTO hof_messages (author, message, written_at)
VALUES (1, 'Youpi ! Je suis au Panthéon !', '2023-12-11');
INSERT INTO user_quests (user_id, quest_id, completed)
VALUES (1, 5, FALSE), (1, 6, TRUE);
INSERT INTO user_unlocked_items (user_id, item_id)
VALUES (1, 10), (1, 100), (1, 1000)
