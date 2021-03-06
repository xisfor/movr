# -*- coding: utf-8 -*-
"""
    Movr
    ~~~~~~
    A chat log move analyser with Flask and sqlite3.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, json, Response

app = Flask(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'movr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    TMP_FOLDER='tmp'
))
app.config.from_envvar('MOVR_SETTINGS', silent=True)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = dict_factory
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

# TODO: seeds

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()
    # db.close()



@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()





# TODO
# list available logs with actions
@app.route('/')
def show_entries():
    return render_template('index.html')



# manage genres
#
# /genres - GET, POST
# /genres/{id}/edit - GET
# /genres/{id} - PUT, DELETE (POST)
@app.route('/genres', methods=['GET'])
def show_genres():
    genres = query_db('select id, name from genres order by id desc')
    return render_template('genres/index.html', genres=genres)

@app.route('/genres', methods=['POST'])
def create_genre():
    execute_db('insert into genres (name) values (?)', [request.form['name']])
    flash('New genre was successfully created')
    return redirect(url_for('show_genres'))

@app.route('/genres/<int:genre_id>/edit', methods=['GET'])
def edit_genre(genre_id):
    genre = query_db('select * from genres where id = ?', [genre_id], one=True)
    return render_template('genres/edit.html', genre=genre)

@app.route('/genres/<int:genre_id>', methods=['PUT', 'DELETE', 'POST'])
def update_genre(genre_id):
    method = request.form.get('_method', 'POST')

    if method == 'PUT':
        execute_db('update genres set name = ? where id = ?', [ request.form['name'], genre_id ])
        flash('Genre was successfully updated')
        return redirect(url_for('show_genres'))

    elif method == 'DELETE':
        execute_db('delete from genres where id = ?', [genre_id])
        flash('Genre was successfully deleted')
        return redirect(url_for('show_genres'))

    else:
        genre = query_db('select * from genres where id = ?', [genre_id], one=True)
        flash('Invalid method')
        return render_template('genres/edit.html', genre=genre)



# manage moves
#
# /genres/{id}/moves - GET, POST
# /genres/{id}/moves/{id}/edit - GET
# /genres/{id}/moves/{id} - PUT, DELETE (POST)
@app.route('/genres/<int:genre_id>/moves', methods=['GET'])
def show_moves(genre_id):
    genre = query_db('select * from genres where id = ?', [genre_id], one=True)
    moves = query_db('select * from moves where genre_id = ? order by id desc', [genre_id])
    return render_template('moves/index.html', genre=genre, moves=moves)

@app.route('/genres/<int:genre_id>/moves', methods=['POST'])
def create_move(genre_id):
    execute_db('insert into moves (name, genre_id) values (?,?)', [request.form['name'], genre_id])
    flash('New move was successfully created')
    return redirect(url_for('show_moves', genre_id=genre_id))

@app.route('/genres/<int:genre_id>/moves/<int:move_id>/edit', methods=['GET'])
def edit_move(genre_id, move_id):
    genre = query_db('select * from genres where id = ?', [genre_id], one=True)
    move = query_db('select * from moves where genre_id = ? and id = ?', [genre_id, move_id], one=True)
    return render_template('moves/edit.html', genre=genre, move=move)

@app.route('/genres/<int:genre_id>/moves/<int:move_id>', methods=['PUT', 'DELETE', 'POST'])
def update_move(genre_id, move_id):
    method = request.form.get('_method', 'POST')

    if method == 'PUT':
        execute_db('update moves set name = ? where genre_id = ? and id = ?',
            [request.form['name'], genre_id, move_id])
        flash('Move was successfully updated')
        return redirect(url_for('show_moves', genre_id=genre_id))

    elif method == 'DELETE':
        execute_db('delete from moves where genre_id = ? and id = ?',
            [genre_id, move_id])
        flash('Move was successfully deleted')
        return redirect(url_for('show_moves', genre_id=genre_id))

    else:
        move = query_db('select * from moves where id = ?', [move_id], one=True)
        flash('Invalid method')
        return render_template('moves/edit.html', move=move)






from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename

from chat_adapters import *

# import chat log
#
# /texts
@app.route('/texts', methods=['GET'])
def show_texts():
    texts = query_db('select *, chats.id as id, name as genre_name from chats '
        ' left join genres on chats.genre_id = genres.id '
        ' order by id desc')
    return render_template('texts/index.html', texts=texts)



@app.route('/texts/new', methods=['GET'])
def new_text():
    return render_template('texts/new.html')

@app.route('/texts', methods=['POST'])
def create_texts():

    # Test for existing title...
    chat_title = request.form['title']
    chat = query_db('select * from chats where title = ?', [chat_title], one=True)

    if chat_title == '':
        flash('A text needs a title')
        return redirect(url_for('new_text'))

    if chat != None:
        flash('A text with this title exists')
        return redirect(url_for('new_text'))

    if 'input_file' not in request.files:
        flash('No file part')
        return redirect(url_for('new_text'))

    file = request.files['input_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('new_text'))

    # No file saving, just grab the contents
    file_contents = file.read()

    # Set chat parser adapter
    if request.form['chat_adapter'] == 'messenger_plus':
        adapter = MessengerPlusAdapter()
    elif request.form['chat_adapter'] == 'csv':
        adapter = CSVAdapter()

    structured_data = adapter.parse_text(file_contents)

    # if we've got this far without falling apart, we may as well go for it!
    db = get_db()
    db.execute('insert into chats (title, session_count, users) values (?,?,?)',
        [chat_title, structured_data['session_count'], ','.join(structured_data['users'])])
    db.commit()

    chat = query_db('select * from chats where title = ?', [chat_title], one=True)
    chat_id = chat['id']

    # create moves
    if 'moves' in structured_data:
        if 'genre_id' in request.form:
            genre_id = request.form['genre_id']
        else:
            genre_name = 'Generated for %s' % request.form['title']
            db.execute('insert into genres (name) values (?)', [genre_name])
            genre = query_db('select * from genres where name = ?', [genre_name], one=True)
            genre_id = genre['id']

        for move in structured_data['moves']:
            db.execute('insert into moves (name, genre_id) values (?,?)', [move, genre_id])

        # regrab the newly inserted moves
        moves = query_db('select * from moves where genre_id = ?', [genre_id])


    cur = db.cursor()
    # create lines
    for line in structured_data['lines']:
        # well, this should thrash the bloody db!
        cur.execute('insert into lines (seq, session, text, time, user, chat_id, client_notification) values (?,?,?,?,?,?,?)',
            [ line['seq'], line['session'], line['text'], line['time'],
                line['user'], chat_id, line['client_notification']])

        # add move to
        if 'moves' in structured_data:
            line_id = cur.lastrowid

            cur.execute('update chats set genre_id = ? where id = ?', [genre_id, chat_id])

            for move in line['moves']:
                move_id = [i['id'] for i in moves if i['name'] == move][0]
                update_line_move(line_id, move_id, True)

    db.commit()

    flash('Text imported')
    return redirect(url_for('show_lines', text_id=chat_id))





@app.route('/texts/<int:text_id>/edit', methods=['GET'])
def edit_text(text_id):
    text = query_db('select * from chats where id = ?', [text_id], one=True)
    genres = query_db('select * from genres')
    return render_template('texts/edit.html', text=text, genres=genres)


@app.route('/texts/<int:text_id>', methods=['PUT', 'DELETE', 'POST'])
def update_text(text_id):
    method = request.form.get('_method', 'POST')

    if method == 'PUT':
        execute_db('update chats set title = ?, genre_id = ? where id = ?',
            [ request.form['title'], request.form['genre'], text_id ])
        flash('Text was successfully updated')
        return redirect(url_for('show_texts'))

    elif method == 'DELETE':
        execute_db('delete from lines where chat_id = ?', [text_id])
        execute_db('delete from chats where id = ?', [text_id])
        flash('Text was successfully deleted')
        return redirect(url_for('show_texts'))



# mark-up chat logs
#
# /chats/{id}/lines - GET, PUT

@app.route('/texts/<int:text_id>/lines', methods=['GET'])
def show_lines(text_id):
    text = query_db('select * from chats where id = ?', [text_id], one=True)
    lines = query_db('select * from lines where chat_id = ? order by seq asc', [text_id])
    moves = query_db('select * from moves where genre_id = ?', [text['genre_id']])

    # FIXME: pretty sure one should be able to do this with a map
    line_ids = []
    for line in lines:
        line_ids.append(int(line['id']))

    line_ids_str = ','.join(map(str, line_ids))
    lines_moves = query_db('select * from line_move where line_id in (%s)' % line_ids_str)

    existing_line_moves = []
    for lm in lines_moves:
        existing_line_moves.append('line_%s,move_%s' % (lm['line_id'], lm['move_id']))

    return render_template('lines/index.html', text=text, lines=lines, moves=moves, existing_line_moves=existing_line_moves)


import re

@app.route('/texts/<int:text_id>/lines', methods=['PUT', 'POST'])
def update_lines(text_id):
    method = request.form.get('_method', 'POST')

    if method == 'PUT':
        form_fields = request.form.to_dict()

        for name, value in form_fields.iteritems():

            # form field names look like "line_1,move_2"
            if "line_" in name and "move_" in name:
                line_str, move_str = name.split(',')

                line_num = int(re.findall(r'\d+', line_str)[0])
                move_num = int(re.findall(r'\d+', move_str)[0])

                # cast to bool
                is_line_move = value in '1'

                update_line_move(line_num, move_num, is_line_move)

        flash('Line moves were successfully updated')
        return redirect(url_for('show_lines', text_id=text_id))


def update_line_move(line_id, move_id, is_lm):

    if is_lm:
        # Create_or_update in sqlite...
        # do some crazy shit to get the line_move.id
        # http://stackoverflow.com/questions/418898/sqlite-upsert-not-insert-or-replace
        execute_db('insert or replace into line_move (id, line_id, move_id) values '
            '((select id from line_move where line_id = ? and move_id = ?),?,?)',
                [line_id, move_id, line_id, move_id])

    else:
        execute_db('delete from line_move where line_id = ? and move_id = ?', [line_id, move_id])


