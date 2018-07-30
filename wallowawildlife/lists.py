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
  return render_template('lists/list.html', types=types,
      creatures=creatures, page_title='All')

@bp.route('/wildlife/<url_text>')
def listByType(url_text):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creatures = db.execute('SELECT * FROM creature').fetchall()
  creaturesDisplayable = []

  title = ''
  # check to see if URL is looking for a valid creature type
  for t in types:
    if url_text == t['url_text']:
      title = t['name']

  # if there's no title, the URL doesn't match possible creature types
  if title == '':
    return redirect(url_for('index'))

  # otherwise, only show the creatures of the desired type
  for c in creatures:
    if (c['type_id'] == url_text):
      creaturesDisplayable.append(c)

  return render_template('lists/list.html', types=types,
      creatures=creaturesDisplayable, page_title=title)

@bp.route('/wildlife/add', methods=['GET','POST'])
def addCreature():
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()

  if request.method == 'POST':
    db.execute('INSERT INTO creature (name_common, name_latin,'
               'description, photo_url, wiki_url, user_id, type_id)'
               'VALUES (?,?,?,?,?,?,?)',
               (request.form['name_common'],
                request.form['name_latin'],
                request.form['description'],
                request.form['photo_url'],
                request.form['wiki_url'],
                1,
                request.form['type_id'],
                )
    )
    db.commit()
    flash("Successfully added " + creature['name_common'])
    return redirect(url_for('lists.listAll'))

  return render_template('/lists/creature_add.html', types=types)

@bp.route('/wildlife/<int:creature_id>/')
def showCreature(creature_id):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creature = db.execute('SELECT * FROM creature WHERE id = ?',
                         (creature_id,)).fetchone()

  return render_template('/lists/creature_show.html', types=types,
                         creature=creature)

@bp.route('/wildlife/<int:creature_id>/edit', methods=['GET','POST'])
def editCreature(creature_id):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creature = db.execute('SELECT * FROM creature WHERE id = ?',
                         (creature_id,)).fetchone()

  if request.method == 'POST':

    # only use new values if they were submitted
    name_common = request.form['name_common']
    name_latin = request.form['name_latin']
    description = request.form['description']
    photo_url = request.form['photo_url']
    wiki_url = request.form['wiki_url']
    user_id = 1
    type_id = request.form['type_id']

    db.execute('UPDATE creature SET name_common = ?,'
               'name_latin = ?, description = ?,'
               'photo_url = ?, wiki_url = ?,'
               'user_id = ?, type_id = ?'
               ' WHERE id = ?',
               (name_common, name_latin, description,
                photo_url, wiki_url, user_id, type_id,
                creature_id)
    )
    db.commit()
    flash("Successfully edited " + creature['name_common'])
    return redirect(url_for('lists.listAll'))

  return render_template('/lists/creature_edit.html', types=types,
                         creature=creature)

@bp.route('/wildlife/<int:creature_id>/delete', methods=['GET','POST'])
def deleteCreature(creature_id):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creature = db.execute('SELECT * FROM creature WHERE id = ?',
                         (creature_id,)).fetchone()

  if request.method == 'POST':
    db.execute('DELETE FROM creature where id = ?', (creature_id,))
    db.commit()
    #flash("Successfully deleted " + creature.name_common)
    return redirect(url_for('lists.listAll'))
  else:
    return render_template('/lists/creature_delete.html', types=types,
                         creature=creature)
