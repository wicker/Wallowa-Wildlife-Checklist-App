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


# use the unhashed gplus_id of the current user in session
# to find the user's id in the 'user' table
# so the lists templates and functions can determine
# authorization for performing CRUD operations
@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')
  if user_id is None:
    g.user_id = None
  else:
    users = get_db().execute('SELECT * FROM user').fetchall()
    user_found_flag = False
    for u in users:
      if check_password_hash(u['gplus_id'], user_id):
        g.user_id = u['id']
        user_found_flag = True
        redirect(url_for('lists.listAll'))

    # otherwise, something went wrong with the session
    # close it and redirect them to the login page
    if not user_found_flag:
      session.clear()
      g.user_id = None

@bp.route('/login', methods=('GET', 'POST'))
def login():
  """Handle the GET and POST methods of user login"""

  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()

  # create and store access token in the session
  if request.method == 'GET':
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    session['state'] = state
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
    session['user_id'] = gplus_id

    # check if the user exists in the user table
    # if not, add the entry
    users = db.execute('SELECT * FROM user').fetchall()
    user_found_flag = False
    for u in users:
      if check_password_hash(u['gplus_id'], gplus_id):
        user_found_flag = True

    if not user_found_flag:
      hashed_gplus_id = generate_password_hash(gplus_id)
      db.execute(
        'INSERT INTO user (gplus_id) VALUES (?)',
        (hashed_gplus_id,)
      )
      db.commit()

    flash("You are now logged in!")
    return redirect(url_for('lists.listAll'))


@bp.route('/logout')
def logout():
  """Handle user logging out"""

  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()

  session.clear()
  flash("You have logged out.")
  return redirect(url_for('lists.listAll'))


def login_required(view):
  """Redirect to the login screen"""
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user_id is None:
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view
