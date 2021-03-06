# Movr

Movr is a chat log move analysis tool for linguists. It is made to allow a
researcher to import chat logs, define genres and moves, and assign those
moves to each line of the chat log. Once a text has been tagged, the researcher
can then produce move map visulisations.

Due to the sensitive nature of some of the original texts, the application is
made to be run in isolation on the researchers machine.


## Setup

As a pre-requisite, your machine will need python and `virtualenv` installed. It
is also assumed that you are using a real unix shell (Mac or Linux). Though you
may well be abe to get it to work fine in Windows.

  - `pip install virtualenv`

Checkout the project and go in to that folder. The following commands should get
you up and running.

Install requirements:

  - `virtualenv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`

Prep app environment:

  - `export FLASK_APP=movr.py`
  - `export FLASK_DEBUG=1` - (optional)

Create a database and run:

  - `flask initdb`
  - `flask run`


## Basic use

Create genres and their corresponding moves, go to texts, pick a chat adapter
and import text. View the lines to markup with the selected genre's moves.


## Tech info

The application uses the python programming language and the [Flask framework](http://flask.pocoo.org/)
to create a web interface and manage actions.

We use an in-situ sqlite3 database to store encoded lines and move information.
To clear this, you can either rerun `flask initdb` to empty it, or just delete
the movr.db file from the project directory.

The application is tested against the data in `_test_`.
