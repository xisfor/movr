# -*- coding: utf-8 -*-
"""
    Movr
    ~~~~~~
    A chat log move analyser with Flask and sqlite3.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

app = Flask(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'movr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('MOVR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
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
    db.close()



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



# import chat log
#
# /chats/new

# mark-up chat logs
#
# /chats/{id}/lines
# /chats/{id}/lines/{id}/edit



@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))









@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))




# if __name__ == "__main__":
#     app.run()
