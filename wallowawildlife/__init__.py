# -*- coding: utf-8 -*-
""" Application Factory

This is the entry point to the entire application.
"""

import os
from flask import Flask

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
    types = db.execute('SELECT name FROM creature_type').fetchall()
    print(types)
    return 'Hello, World!'

  # register cli db commands
  from . import db
  db.init_app(app)

  # apply blueprints
  from . import auth
  app.register_blueprint(auth.bp)

  # possibly add a url rule handling '/' for index
  # make url_for('index') == url_for('blog.index')
  # in another app, you might define a separate main index here with
  # app.route, while giving the blog blueprint a url_prefix, but for
  # the tutorial the blog will be the main index
  app.add_url_rule('/', endpoint='index')

  return app
