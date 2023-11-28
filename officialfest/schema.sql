DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS hof_messages;
DROP TABLE IF EXISTS user_unlocked_items;
DROP TABLE IF EXISTS user_quests;
DROP TABLE IF EXISTS hof_messages;
DROP TABLE IF EXISTS forum_themes;
DROP TABLE IF EXISTS forum_threads;
DROP TABLE IF EXISTS forum_messages;

CREATE TABLE users (
    user_id INTEGER NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT,
    best_score INTEGER NOT NULL DEFAULT 0,
    weekly_best_score INTEGER NOT NULL DEFAULT 0,
    best_level INTEGER DEFAULT NULL,
    has_carrot BOOLEAN NOT NULL DEFAULT FALSE,
    pyramid_step INTEGER NOT NULL DEFAULT 4,
    pyramid_rank INTEGER NOT NULL,
    is_moderator BOOLEAN NOT NULL DEFAULT FALSE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE hof_messages (
    author INTEGER NOT NULL PRIMARY KEY,
    message TEXT NOT NULL,
    written_at DATETIME NOT NULL,
    FOREIGN KEY (author) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE user_unlocked_items (
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE user_quests (
    user_id INTEGER NOT NULL,
    quest_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user_id, quest_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
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
    FOREIGN KEY (theme_id) REFERENCES forum_themes (theme_id) ON DELETE CASCADE,
    FOREIGN KEY (author) REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE TABLE forum_messages (
    message_id INTEGER NOT NULL PRIMARY KEY,
    thread_id INTEGER NOT NULL,
    author INTEGER NOT NULL,
    html_content TEXT NOT NULL,
    created_at DATETIME not NULL,
    FOREIGN KEY (thread_id) REFERENCES forum_threads (thread_id) ON DELETE CASCADE,
    FOREIGN KEY (author) REFERENCES users (user_id) ON DELETE CASCADE
);

INSERT INTO users (user_id, username, email, best_score, weekly_best_score, best_level, has_carrot, pyramid_step, pyramid_rank, is_moderator, is_admin)
VALUES (0, 'Igor', 'igor@hammerfest.fr', 19999999, 0, 115, TRUE, 2, 999, TRUE, TRUE);
INSERT INTO hof_messages (author, message, written_at)
VALUES (0, 'Hammerfest !! Yeaaaaaaaaah !', '2023-12-11');
/*
INSERT INTO forum_themes (theme_id, name, description, is_restricted)
VALUES (2, "Caverne de l'apprenti", "Si vous vous etes perdu(e) dans les Cavernes, c'est ici qu'il faut demander sa route", FALSE),
       (10, "Coin des modos", "Vous n'avez rien à faire là !", TRUE);
INSERT INTO forum_threads (thread_id, theme_id, author, name, total_messages, is_sticky, is_closed)
VALUES (0, 2, 0, 'Réactions du Jour', 22, FALSE, FALSE),
       (1, 2, 0, 'Les Antiquaires Polaires', 1, FALSE, FALSE),
       (3, 2, 0, 'Règlement Général du Forum', 1, TRUE, FALSE);
INSERT INTO forum_messages (thread_id, author, html_content, created_at)
VALUES (0, 0, 'Ma première réaction.', '2023-12-11 10:00:00'),
       (0, 0, 'Ma deuxième réaction.', '2023-12-11 11:01:00'),
       (1, 0, 'G le pad.', '2023-12-12 05:30:00'),
       (0, 0, 'Spam 1 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 2 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 3 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 4 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 5 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 6 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 7 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 8 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 9 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 10 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 11 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 12 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 13 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 14 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 15 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 16 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 17 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 18 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 19 !', '2023-12-12 08:00:00'),
       (0, 0, 'Spam 20 !', '2023-12-12 08:00:00'),
       (3, 0, 'Le règlement est...', '2024-01-01');
*/
