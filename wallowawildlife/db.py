# -*- coding: utf-8 -*-
"""Database Functions

This module describes functions for initializing and
accessing the sqlite database.
"""

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

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
  types = [('Mammal','mammal'),
           ('Bird','bird'),
           ('Reptile/Amphibian','reptile_amphibian'),
           ('Tree/Shrub','tree_shrub'),
           ('Fish','fish'),
           ('Wildflower','wildflower'),
           ('Spider/Insect','spider_insect')]
  for t in types:
    db.execute(
        'INSERT INTO creature_type (name, url_text) VALUES (?,?)',
        (t[0],t[1]))
    db.commit()

    with open('db.csv', 'r') as f:
      for line in f:
        line = line.split(',')

        # convert type_id from text to integer
        if line[2] == 'mammal':
          line[2] = 1
        elif line[2] == 'bird':
          line[2] = 2
        elif line[2] == 'reptile_amphibian':
          line[2] = 3
        elif line[2] == 'tree_shrub':
          line[2] = 4
        elif line[2] == 'fish':
          line[2] = 5
        elif line[2] == 'wildflower':
          line[2] = 6
        elif line[2] == 'spider_insect':
          line[2] = 7

        # load this into the right table
        # user id of '1' is 'admin' user
        db.execute('INSERT INTO creature (name_common, \
                                          name_latin,  \
                                          type_id,     \
                                          description, \
                                          photo_url,   \
                                          wiki_url,    \
                                          user_id)     \
          VALUES (?,?,?,?,?,?,?)',
          (line[0], line[1], line[2],
           line[3], line[4], line[5], 1)
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
