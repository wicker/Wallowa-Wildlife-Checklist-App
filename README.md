# Wallowa Wildlife Checklist App

This app uses the Python-based microframework Flask and an SQLite3 database to allow users to log in and maintain wildlife checklists for Wallowa County. The database model supports users, checklists, types of creatures, and the creatures themselves. The Flask app builds the database from a .csv file so it is adaptable to any other location, real or imagined. 

1. Clone the repo 
1. Create the python virtual environment
1. Run pip install -r requirements.txt
1. Initialize the db with `flask initdb`
1. Start the app with `flask run`
1. Navigate to the app in the browser

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


