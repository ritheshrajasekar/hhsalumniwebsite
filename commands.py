# import click
# from flask.cli import with_appcontext
# from app import db

# @click.command(name='create_tables')
# @with_appcontext
# def create_tables():
#  db.create_all()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import *


app = Flask(__name__)
DB_NAME = "database_2.db"
UPLOAD_FOLDER = './static/images/profile_pics'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
db.create_all(app=app)