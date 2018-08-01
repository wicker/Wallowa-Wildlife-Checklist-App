# -*- coding: utf-8 -*-
"""Database Functions

This module describes functions for initializing and
accessing the sqlite database.
"""

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

def get_db():
  """Make the database available in current app context"""
  if 'db' not in g:
    g.db = sqlite3.connect(
      current_app.config['DATABASE'],
      detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory = sqlite3.Row

  return g.db


def close_db(e=None):
  """Remove database from current app context"""
  db = g.pop('db', None)

  if db is not None:
    db.close()


def init_db():
  """Create the database from the schema
     and populate it with the input CSV
  """
  db = get_db()

  with current_app.open_resource('schema.sql') as f:
    db.executescript(f.read().decode('utf-8'))

  # manually add list of creature types
  types = [('Mammals','mammal'),
           ('Birds','bird'),
           ('Reptiles & Amphibians','reptile_amphibian'),
           ('Trees & Shrubs','tree_shrub'),
           ('Fishes','fish'),
           ('Wildflowers','wildflower'),
           ('Spiders & Insects','spider_insect')]
  for t in types:
    db.execute(
      'INSERT INTO creature_type (name, url_text) VALUES (?,?)',
      (t[0],t[1]))
    db.commit()

  # load the list of creatures from the CSV file
  with open('db.csv', 'r') as f:
    for line in f:
      line = line.split(',')

      # load this into the right table
      # user id of '1' is 'admin' user
      db.execute('INSERT INTO creature (name_common, \
                                        name_latin,  \
                                        type_id,     \
                                        photo_url,   \
                                        photo_attr,    \
                                        wiki_url,    \
                                        user_id)     \
        VALUES (?,?,?,?,?,?,?)',
        (line[0], line[1], line[2],
         line[3], line[4], line[5], 1)
      )
      db.commit()

  # manually add the admin user
  db.execute(
    'INSERT INTO user (gplus_id) VALUES (?)',
    (generate_password_hash('adminpass'),)
  )
  db.commit()


@click.command('initdb')
@with_appcontext
def init_db_command():
  """Clear the existing data and create new tables"""
  init_db()
  click.echo('Database initialized.')


def init_app(app):
  """Take the application and register the function"""
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)
