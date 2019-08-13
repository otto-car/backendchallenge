# App Info
This app was built on Ubuntu 19.04 using PyCharm IDE. Ideally I will have time to deploy this app to AWS server with Linux environment.
# Installation notes
## Update repo's
sudo apt-get update
## PostgreSQL
sudo apt-get install postgresql
## psycopg2 - PostgreSQL wrapper for Flask
sudo apt-get install python-psycopg2
## libpq - postgresql interface
sudo apt-get install libp
## Python3 dependencies
flask flask-sqlalchemy psycopg2 flask-migrate flask-script

# PostgreSQL Setup
## Set Up User
## Create Database
## Migrate Database
python manage.py db init
python manage.py db migrate
python manage.py db upgrade 

# Running the app
source environment.env + flask run

