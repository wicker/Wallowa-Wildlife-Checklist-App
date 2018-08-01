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
@login_required
def addCreature():
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()

  if request.method == 'POST':
    db.execute('INSERT INTO creature (name_common, name_latin,'
               'photo_attr, photo_url, wiki_url, user_id, type_id)'
               'VALUES (?,?,?,?,?,?,?)',
               (request.form['name_common'],
                request.form['name_latin'],
                request.form['photo_attr'],
                request.form['photo_url'],
                request.form['wiki_url'],
                g.user_id,
                request.form['type_id'],
                )
    )
    db.commit()
    flash("Successfully added " + request.form['name_common'])
    return redirect(url_for('lists.listAll'))

  return render_template('/lists/creature_add.html', types=types)

@bp.route('/wildlife/<int:creature_id>/')
def showCreature(creature_id):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creature = db.execute('SELECT * FROM creature WHERE id = ?',
                         (creature_id,)).fetchone()

  if creature:
    return render_template('/lists/creature_show.html', types=types,
                           creature=creature)
  else:
    flash("This entry does not exist.")
    return redirect(url_for('lists.listAll'))

@bp.route('/wildlife/<int:creature_id>/edit', methods=['GET','POST'])
@login_required
def editCreature(creature_id):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creature = db.execute('SELECT * FROM creature WHERE id = ?',
                         (creature_id,)).fetchone()

  if g.user_id is not creature['user_id']:
    flash("You may only edit an entry you own.")
    return redirect(url_for('lists.listAll'))

  if request.method == 'POST':

    # only use new values if they were submitted
    if request.form['name_common']:
      name_common = request.form['name_common']
    else:
      name_common = creature['name_common']

    if request.form['name_latin']:
      name_latin = request.form['name_latin']
    else:
      name_latin = creature['name_latin']

    if request.form['photo_attr']:
      photo_attr = request.form['photo_attr']
    else:
      photo_attr = creature['photo_attr']

    if request.form['photo_url']:
      photo_url = request.form['photo_url']
    else:
      photo_url = creature['photo_url']

    if request.form['wiki_url']:
      wiki_url = request.form['wiki_url']
    else:
      wiki_url = creature['wiki_url']

    if request.form['type_id']:
      type_id = request.form['type_id']
    else:
      type_id = creature['type_id']

    user_id = creature['user_id']

    db.execute('UPDATE creature SET name_common = ?,'
               'name_latin = ?, photo_attr = ?,'
               'photo_url = ?, wiki_url = ?,'
               'user_id = ?, type_id = ?'
               ' WHERE id = ?',
               (name_common, name_latin, photo_attr,
                photo_url, wiki_url, user_id, type_id,
                creature_id)
    )
    db.commit()
    flash("Successfully edited " + creature['name_common'])
    return redirect(url_for('lists.listAll'))

  return render_template('/lists/creature_edit.html', types=types,
                         creature=creature)

@bp.route('/wildlife/<int:creature_id>/delete', methods=['GET','POST'])
@login_required
def deleteCreature(creature_id):
  db = get_db()
  types = db.execute('SELECT * FROM creature_type').fetchall()
  creature = db.execute('SELECT * FROM creature WHERE id = ?',
                         (creature_id,)).fetchone()

  if g.user_id is not creature['user_id']:
    flash("You may only delete an entry you own.")
    return redirect(url_for('lists.listAll'))

  if request.method == 'POST':
    db.execute('DELETE FROM creature where id = ?', (creature_id,))
    db.commit()
    flash("Successfully deleted " + creature['name_common'])
    return redirect(url_for('lists.listAll'))

  return render_template('/lists/creature_delete.html', types=types,
                         creature=creature)
