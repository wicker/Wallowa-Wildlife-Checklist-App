# -*- coding: utf-8 -*-
"""Lists Blueprint

This module describes the blueprint for functions in a Flask app
which display and allow the user to manipulate lists of creatures.

These functions were copied over verbatim from the flaskr tutorial
before being modified for this application.
"""

from flask import (
  Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from wallowawildlife.auth import login_required
from wallowawildlife.db import get_db

bp = Blueprint('lists', __name__)

@bp.route('/wildlife')
def listAll():
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creatures = db.execute('SELECT * FROM creature').fetchall()
  return render_template('lists/list_all.html', types=types, creatures=creatures)

@bp.route('/wildlife/<url_text>')
def listByType(url_text):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creatures = db.execute('SELECT * FROM creature').fetchall()
  creaturesDisplayable = []

  if url_text == 'spider_insect':
    title = 'Spiders/Insects'
  elif url_text == 'reptile_amphibian':
    title = 'Reptiles/Amphibians'
  elif url_text == 'tree_shrub':
    title = 'Tree/Shrub'
  elif url_text == 'fish':
    title = 'Fishes'
  else:
    title = url_text.capitalize() + 's'

  for c in creatures:
    if (c['type_id'] == url_text):
      creaturesDisplayable.append(c)

  return render_template('lists/list_by_type.html', types=types,
      creatures=creaturesDisplayable, page_title=title)

