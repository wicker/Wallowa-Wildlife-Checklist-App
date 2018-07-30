# Wallowa Wildlife Checklist App

This app uses the Python-based microframework Flask and an SQLite3 database to allow users to log in and maintain wildlife checklists for Wallowa County. The database model supports users, checklists, types of creatures, and the creatures themselves. The Flask app builds the database from a .csv file so it is adaptable to any other location, real or imagined. 

The app is architected as an application factory using blueprints and test coverage. It was developed using the [Flaskr tutorial](http://flask.pocoo.org/docs/1.0/tutorial/) as a guide to these new features in Flask.

## Install

Clone the git repository.

```
https://github.com/wicker/Wallowa-Wildlife-Checklist-App.git
```

Create the Python [virtual environment](https://virtualenvwrapper.readthedocs.io/en/latest/).

```
mkvirtualenv wallowa
workon wallowa
```

Install the app.

```
pip install -e .
```

## Run

```
export FLASK_APP=wallowawildlife
export FLASK_ENV=development
flask initdb
flask run
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in a browser.

## Test

```
pip install '.[test]'
pytest
```

Run with a coverage report.

```
coverage run -m pytest
coverage report
coverage html  # open htmlcov/index.html in a browser
```

# Docs and Design Notes

## Database Schema

![Database schema](docs/db-schema.png)

## Populating the Database

The `creature_type` table is manually populated by `flask initdb`.

|id|name|url_text|
|--|----|--------|
|1|Mammal|mammal|
|2|Bird|bird|
|3|Reptile/Amphibian|reptile_amphibian|
|4|Tree/Shrub|tree_shrub|
|5|Fish|fish|
|6|Wildflower|wildflower|
|7|Spider/Insect|spider_insect|

The `creature` table is populated by a CSV file called db.csv. The program expects it will take this format: 

|Fields|Example|
|------|-------|
|Common Name|Rocky Mountain Elk|
|Latin Name|Cervus canadensis|
|Type|mammal|
|Description|One of the largest land mammals, elk range in forest and forest-edge habitats.|
|Photo URL|https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Rocky_Mountain_Bull_Elk.jpg/1024px-Rocky_Mountain_Bull_Elk.jpg|
|Wiki URL|https://en.wikipedia.org/wiki/Elk|

The `Type` entry must match one of the `url_text` entries in the `creature_type` table above.

All creatures initialized by the db are owned by the admin user with id `1` and may not be edited or deleted by non-admin users.

The `user` table is set up with an admin and a user account.

## Blueprints, Routes, and Templates

|Blueprint|Route|Route Handler|Template|
|---------|-----|-------------|--------|
|~|/|index()|front_page.html|
|Auth|/register|register()|auth/register.html|
|Auth|/login|login()|auth/login.html|
|Auth|/logout|logout()|~|
|Lists|/wildlife|listAll()|lists/list_all.html|
|Lists|/wildlife/?t=mammals|listByType()|list_by_type.html|
|Lists|/wildlife/add|addCreature()|creature_add.html|
|Lists|/wildlife/mammals/10|showCreature()|creature_show.html|
|Lists|/wildlife/mammals/10/edit|editCreature()|creature_edit.html|
|Lists|/wildlife/mammals/10/delete|deleteCreature()|creature_delete.html|

## Set up Wallowa Wildlife Production Site

Set A records for `@` and `www` to point wallowawildlife.com the EC2 public IP.  

Set up keys between dev laptop and the server.

```
sudo apt update
sudo apt upgrade
sudo apt install python3-pip python3-dev nginx
sudo pip3 install virtualenv 
```

Create the app folders and the virtual environment:

```
mkdir ~/public/wallowawildlife.com
cd ~/public/wallowawildlife.com
virtualenv wallowa-venv
source wallowa-venv/bin/activate
pip install uwsgi flask
deactivate
```

Now to set up the basic Flask application.

```
vim ~/public/wallowawildlife.com/wallowawildlife.py
```

```
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Wallowa Wildlife"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
```

Create the WSGI entry point.

```
vim ~/public/wallowawildlife.com/wsgi.py
```

```
from myproject import app

if __name__ == "__main__":
    app.run()
```

The uWSGI config file will set up the socket.

```
vim ~/public/wallowawildlife.com/wallowawildlife.ini
```

```
[uwsgi]
module = wsgi:app

master = true
processes = 5

socket = wallowawildlife.sock
chmod-socket = 660
vacuum = true

die-on-term = true
```

Next, set up the systemd service unit file so the server will start the app when it boots.

```
sudo vim /etc/systemd/system/wallowawildlife.service
```

```
[Unit]
Description=uWSGI instance to serve Wallowa Wildlife Checklists App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/public/wallowawildlife.com
Environment="PATH=/home/ubuntu/public/wallowawildlife.com/wallowa-venv/bin"
ExecStart=/home/ubuntu/public/wallowawildlife.com/wallowa-venv/bin/uwsgi --ini wallowawildlife.ini

[Install]
WantedBy=multi-user.target
```

Then start the service.

```
sudo systemctl start wallowawildlife
sudo systemctl enable wallowawlidlife
```

Configure Nginx to proxy requests.

```
sudo vim /etc/nginx/sites-available/wallowawildlife.com
```

```
server {
  listen 80;
  server_name wallowawildlife.com;

  location / {
    include uwsgi_params;
    uwsgi_pass unix:///home/ubuntu/public/wallowawildlife.com/wallowawildlife.sock;
  }
}
```

Then enable and test the Nginx server block configuration.

```
sudo ln -s /etc/nginx/sites-available/wallowawildlife.com /etc/nginx/sites-enabled
sudo nginx -t 
sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'
```

The relevant ports (80, 443) should already be enabled in Amazon's EC2 security groups settings. 

The app should be visible at `http://wallowawildlife.com`.

## Use Flaskr Tutorial

Continuous Integration/Deployment with Flask

Flask blueprints and factories


