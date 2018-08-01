# -*- coding: utf-8 -*-
""" Application Factory

This is the entry point to the entire application.
"""

import os, json
from flask import Flask, render_template, jsonify, flash, redirect, url_for

def create_app(test_config=None):
  """Create an instance of Wallowa Wildlife Checklists"""
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    # This secret will be overriden with the instance config.
    SECRET_KEY='dev',
    # Store the database in the instance folder.
    DATABASE=os.path.join(app.instance_path, 'wallowawildlife.sqlite'),
    # Read in the client_id for google login.
    CLIENT_ID = json.loads(
      open('wallowawildlife/client_secrets.json', 'r').read())['web']['client_id']
  )

  if test_config is None:
    # Load the instance config.
    app.config.from_pyfile('config.py', silent=True)
  else:
    # Otherwise, load the test config.
    app.config.update(test_config)

  # Make the instance folder if it doesn't exist.
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  # Make the database available.
  from wallowawildlife.db import get_db


  @app.route('/')
  def index():
    """Handle the index route"""
    db = get_db()
    types = db.execute('SELECT * FROM creature_type').fetchall()
    return render_template('front_page.html', types=types)


  @app.route('/wildlife/JSON')
  def wildlifeJSON():
    """Create JSON endpoint"""
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


  @app.errorhandler(404)
  def page_not_found(e):
    """Redirect from all unhandled URLs to the index route"""
    return redirect(url_for('index'))


  # Register cli db commands.
  from . import db
  db.init_app(app)

  # Apply blueprints.
  from . import auth
  app.register_blueprint(auth.bp)

  from . import lists
  app.register_blueprint(lists.bp)
  app.add_url_rule('/', endpoint='index')

  return app
