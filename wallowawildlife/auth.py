# -*- coding: utf-8 -*-
"""Auth Blueprint

This module describes the blueprint for authorization-related
functions for a Flask app.

These functions were copied over verbatim from the flaskr tutorial
before being modified for this application.
"""

import functools

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from wallowawildlife.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
  """Handle the GET and POST methods of user registration"""

  db = get_db()
  types = db.execute('SELECT name FROM creature_type').fetchall()

  if request.method == 'POST':
    name = request.form['name']
    password = request.form['password']
    db = get_db()
    error = None

    if not name:
      error = 'Username is required.'
    elif not password:
      error = 'Password is required.'
    elif db.execute(
        'SELECT id FROM user WHERE name = ?', (name,)
    ).fetchone() is not None:
      error = 'User {} is already registered.'.format(name)

    if error is None:
      db.execute(
        'INSERT INTO user (name, password) VALUES (?, ?)',
        (name, generate_password_hash(password))
      )
      db.commit()
      return redirect(url_for('auth.login'))

    flash(error)

  return render_template('auth/register.html',types=types)


@bp.route('/login', methods=('GET', 'POST'))
def login():
  """Handle the GET and POST methods of user login"""

  db = get_db()
  types = db.execute('SELECT name FROM creature_type').fetchall()

  if request.method == 'POST':
    name = request.form['name']
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
      'SELECT * FROM user WHERE name = ?', (name,)
    ).fetchone()

    if user is None:
      error = 'Incorrect name.'
    elif not check_password_hash(user['password'], password):
      error = 'Incorrect password.'

    if error is None:
      session.clear()
      session['user_id'] = user['id']
      return redirect(url_for('index'))

    flash(error)

  return render_template('auth/login.html',types=types)


@bp.route('/logout')
def logout():
  """Handle user logging out"""

  db = get_db()
  types = db.execute('SELECT name FROM creature_type').fetchall()

  session.clear()
  return redirect(url_for('index'))


def login_required(view):
  """Redirect to the login screen"""
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view
