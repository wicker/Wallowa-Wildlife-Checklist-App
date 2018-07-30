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

@bp.route('/all')
def list_all():
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creatures = db.execute('SELECT * FROM creature').fetchall()
  return render_template('lists/list_all.html', types=types, creatures=creatures)

