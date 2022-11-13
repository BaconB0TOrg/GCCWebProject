import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.models import models_init

scriptdir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(scriptdir, 'server_hosting.sqlite3')
os.environ["dbpath"] = dbpath

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
  if models_init():
    print("database created!")
  else:
    print("databse already up.")

  