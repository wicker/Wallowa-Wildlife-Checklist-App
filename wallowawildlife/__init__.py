# -*- coding: utf-8 -*-
""" Application Factory

This is the entry point to the entire application.
"""

import os
from flask import Flask
from flask import render_template

def create_app(test_config=None):
  """Create an instance of Wallowa Wildlife Checklists"""
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    # this secret will be overriden with the instance config
    SECRET_KEY='test',
    # store the database in the instance folder
    DATABASE=os.path.join(app.instance_path, 'wallowawildlife.sqlite')
  )

  if test_config is None:
    # just load the instance config
    app.config.from_pyfile('config.py', silent=True)
  else:
    # otherwise, load the test config
    app.config.update(test_config)

  # make the instance folder if it doesn't exist
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  from wallowawildlife.db import get_db

  @app.route('/hello')
  def route_hello():
    db = get_db()
    creatures = db.execute('SELECT * FROM creature').fetchall()
    for c in creatures:
      print(c['name_common'])
    users = db.execute('SELECT * FROM user').fetchall()
    for u in users:
      print(u['id'],u['name'],u['password'])
    return 'Hello, World!'

  @app.route('/')
  def index():
    db = get_db()
    types = db.execute('SELECT * FROM creature_type').fetchall()
    return render_template('front_page.html', types=types)

  # register cli db commands
  from . import db
  db.init_app(app)

  # apply blueprints
  from . import auth
  app.register_blueprint(auth.bp)

  from . import lists
  app.register_blueprint(lists.bp)
  app.add_url_rule('/', endpoint='index')

  return app
