# -*- coding: utf-8 -*-
"""Auth Blueprint

This module describes the blueprint for authorization-related
functions for a Flask app.

These functions were copied over verbatim from the flaskr tutorial
before being modified for this application.
"""

import functools, random, string, httplib2, json, requests
from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for,
  current_app as app
)
from werkzeug.security import check_password_hash, generate_password_hash
from wallowawildlife.db import get_db

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')

  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
  """Handle the GET and POST methods of user registration"""

  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()

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
  types = db.execute('SELECT * FROM creature_type').fetchall()

  # create and store access token in the session
  if request.method == 'GET':
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    session['state'] = state
    flash(session['state']+'\n'+app.config['CLIENT_ID'])
    return render_template('auth/login.html',types=types,
                           glogin=True, STATE=state)

  # the user has logged in with google
  elif request.method == 'POST':
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(app.root_path+'/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != app.config['CLIENT_ID']:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print("done!")
    return output


@bp.route('/logout')
def logout():
  """Handle user logging out"""

  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()

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
