import os
from flask import Flask

def create_app(test_config=None):
  """Create an instance of Wallowa Wildlife Checklists"""
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    # this secret will be overriden with the instance config
    SECRET_KEY='test',
    # store the database in the instance folder
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
  )

  if test_config is None:
    # just load the instance config
    app.config.from_pyfile('config.py', silent=True)
  else:
    # otherwise, load the test config
    app.config.pdate(test_config)

  # make the instance folder if it doesn't exist
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass

  @app.route('/test')
  def route_test():
    return 'We exist!'

  # register cli db commands
  from . import db
  db.init_app(app)

  # apply blueprints
  from . import auth
  app.register_blueprint(auth.bp)

  # possibly add a url rule handling '/' for index

  return app
