# -*- coding: utf-8 -*-
""" Application Factory

This is the entry point to the entire application.
"""

import os
from flask import Flask, render_template, jsonify

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

  @app.route('/')
  def index():
    db = get_db()
    types = db.execute('SELECT * FROM creature_type').fetchall()
    return render_template('front_page.html', types=types)

  @app.route('/wildlife/JSON')
  def wildlifeJSON():
    db = get_db()
    creatures = db.execute('SELECT * FROM creature').fetchall()
    json_creatures = [{'id':c['id'],
                       'name_common':c['name_common'],
                       'name_latin':c['name_latin'],
                       'photo_url':c['photo_url'],
                       'photo_attr':c['photo_attr'],
                       'wiki_url':c['wiki_url'],
                       'type':c['type_id']} for c in creatures]

    return jsonify(json_creatures)

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
