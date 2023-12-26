# Officialfest

This is a fan-made, read-only Flask version of the old [Hammerfest](https://fr.wikipedia.org/wiki/Hammerfest_(jeu_vid%C3%A9o)) website written in Flask with a sqlite3 database.

The original PHP website and Flash game were made by [Motion Twin](https://motiontwin.com/fr/). Hammerfest was closed in November 2023.

It's not possible to play the original game with this server because the game-related backend is not implemented.

If you want to play Hammerfest, you can go to [Eternalfest](https://eternalfest.net/) where you can play the original levels and many more! You can join the [Hammerfest Discord](https://discord.com/invite/VTBjxn7) too.

# Running the server

## Prerequisites

Python3 is required to run the server.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# If you want to run the server in ES or EN language, you must compile translations
pybabel compile -d officialfest/translations/
```

## Creating the database

The SQL file `officialfest/schema.sql` contains a script to initialize the sqlite3 database.

You can initialize the database from from scratch with the following command:

```bash
flask --app officialfest init-db
```

## Starting the server

You can start the server in a few different ways.

Using Flask development server:

```bash
flask --app officialfest run
```

Using the Gunicorn HTTP WSGI server:

```bash
gunicorn 'officialfest:create_app()'
```

# Features

## Implemented

- most of the original pages / routes are implemented,
- most if not all static content (images, css, etc.) should be there too,
- access to user public data through /user.html/[id]
- access to public forum threads and messages
- access to public rankings

## Features that will not be implemented 

Again, you will not be able to play the game with this server. Also, since this is only a read-only version, you also cannot:

- create or delete an account,
- login / logout (sessions are not implemented),
- post new threads and messages in the forum,
- improve your score, go up the rankings, etc. anything related to playing the actual game.

## Other differences with the original website

- user profile doesn't show email address
- banner shows non-affiliation with Motion Twin
- forum displays the year when a message was posted
- search function parameters include author and dates
- search function results lead to the right thread page
- search function results show date
- search function results include a previsualisation item
- timeattack score is always displayed correctly

## TODO

- Implement access to private forum themes
- Add missing ES / EN translations
