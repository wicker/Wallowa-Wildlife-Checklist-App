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
  """Create the database from the schema"""
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
